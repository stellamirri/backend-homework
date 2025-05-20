import json
from flask import Flask, request, redirect, render_template 
from flask import request 
from flask import redirect, render_template 
import requests 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.sql import text
from flask_cors import CORS
from datetime import datetime as DateTime
from flask import request
from flask import render_template
from flask import redirect
from flask_socketio import SocketIO
from flask_socketio import emit


app = Flask(__name__)  #on crée une application WEB avec Flask
socketio = SocketIO(app)
CORS(app)


db_name = 'notes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  #on crée une connexion entre Flask et la base de données accessible grâce à SQLite

# MODELE NOTE
class Note(db.Model):  #on crée un modèle de base de données qui se comporte comme une table SQL, grâce à ce que SQLAlchemy (via db.Model) sait déjà faire
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
    # Émettre un événement 'note_updated' à tous les clients
    socketio.emit('note_updated', {
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'done': note.done
    })
    return dict(id=note.id, done=note.done)

@app.route('/front/notes')
def front_notes():
    url = request.url_root + 'api/notes'
    req = requests.get(url)
    if not req.ok:
        return dict(error="Failed to fetch notes", status=req.status_code)
    notes = req.json()
    return render_template('notes.html.j2', notes=notes)



@socketio.on('connect-ack')
def connect_ack(message):
    print(f'received ACK message: {message} of type {type(message)}')
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
