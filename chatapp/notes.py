import json
from flask import Flask, request, redirect, render_template
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
VERSION = "01"

db_name = 'notes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELE NOTE
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    done = db.Column(db.Boolean)

# CREATION DES TABLES
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/front/notes')

@app.route('/db/alive')
def db_alive():
    try:
        db.session.execute(text('SELECT 1'))
        return dict(status="healthy", message="Database connection is alive")
    except Exception as e:
        return dict(error=str(e))

@app.route('/api/version')
def version():
    return dict(version=VERSION)

# ENDPOINTS NOTES

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.all()
    return [dict(id=n.id, title=n.title, content=n.content, done=n.done) for n in notes]

@app.route('/api/notes', methods=['POST'])
def create_note():
    try:
        data = json.loads(request.data)
        note = Note(title=data['title'], content=data['content'], done=False)
        db.session.add(note)
        db.session.commit()
        return dict(id=note.id, title=note.title, content=note.content, done=note.done)
    except Exception as e:
        return dict(error=str(e)), 422

@app.route('/api/notes/<int:id>/done', methods=['POST'])
def mark_note_done(id):
    note = Note.query.get(id)
    if not note:
        return dict(error="Note not found"), 404
    note.done = True
    db.session.commit()
    return dict(id=note.id, done=note.done)

@app.route('/front/notes')
def front_notes():
    url = request.url_root + 'api/notes'
    req = requests.get(url)
    if not req.ok:
        return dict(error="Failed to fetch notes", status=req.status_code)
    notes = req.json()
    return render_template('notes.html.j2', notes=notes, version=VERSION)

if __name__ == '__main__':
    app.run(debug=True)
