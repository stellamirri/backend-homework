import pathlib as pl

import numpy as np
import pandas as pd
import csv


from flask import Flask, jsonify, request
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

## DB declaration

# filename where to store stuff (sqlite is file-based)

db_name = 'chat.db'
# how do we connect to the database ?
# here we say it's by looking in a file named chat.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)



app = Flask(__name__)
CORS(app)

data = pl.Path(__file__).parent.absolute() / 'data'

# Charger les données CSV
associations_df = pd.read_csv(data / 'associations_etudiantes.csv')
evenements_df = pd.read_csv(data / 'evenements_associations.csv')

## Vous devez ajouter les routes ici : 
#* Endpoint : `/api/alive`
#* Méthode : GET
#* Description : Vérifie si le serveur est en fonctionnement.
#* Réponse :
# + 200 OK : { "message": "Alive" }

@app.route('/api/alive', methods=['GET'])     
def api_alive():
    return { "message": "Alive" }, 200

## Liste de toutes les associations

#* Endpoint : `/api/associations`
#* Méthode : GET
#* Description : Retourne une liste de toutes les associations.
#* Réponse :
#  + 200 OK : Liste des ids des associations.


@app.route('/api/associations', methods=['GET'])
def api_associations():
    ids = associations_df['id'].tolist()
    return ids, 200

## Détails d'une association

# * Endpoint : `/api/association/<int:id>`
# * Méthode : GET
# * Description : Retourne les détails d'une association spécifique par son ID.
# * Réponse :
#   + 200 OK : Détails de l'association demandée.
#   + 404 Not Found : { "error": "Association not found" }

@app.route('/api/association/<int:id>', methods=['GET'])
def description(id):
    row = associations_df[associations_df['id'] == id]
    if not row.empty:
        r = row.iloc[0]
        return {
            "id": int(r['id']),
            "nom": r['nom'],
            "type": r['type'],
            "description": r['description']
        }, 200
    return { "error": "Event not found" }, 404


## Liste de tous les événements

# * Endpoint : `/api/evenements`
# * Méthode : GET
# * Description : Retourne une liste de tous les événements.
# * Réponse :
#   + 200 OK : Liste des ids des événements.


@app.route('/api/evenements', methods=['GET'])
def events():
    ids = evenements_df['id'].tolist()
    return ids, 200


# ## Détails d'un événement

# * Endpoint : `/api/evenement/<int:id>`
# * Méthode : GET
# * Description : Retourne les détails d'un événement spécifique par son ID.
# * Réponse :
#   + 200 OK : Détails de l'événement demandé.
#   + 404 Not Found : { "error": "Event not found" }

@app.route('/api/evenement/<int:id>', methods=['GET'])
def description2(id):
    row = evenements_df[evenements_df['id'] == id]
    if not row.empty:
        r = row.iloc[0]
        return {
            "id": int(r['id']),
            "association_id": int(r['association_id']),
            "nom": r['nom'],
            "date": r['date'],
            "lieu": r['lieu'],
            "description": r['description']
        }, 200
    return { "error": "Event not found" }, 404

# ## Liste des événements d'une association

# * Endpoint : `/api/association/<int:id>/evenements`
# * Méthode : GET
# * Description : Retourne une liste des événements organisés par une association spécifique.
# * Réponse :
#   + 200 OK : Liste des événements de l'association demandée.

@app.route('/api/association/<int:id>/evenements', methods=['GET'])
def event_asso(id):
    bon_id = evenements_df[evenements_df['association_id'] == id]
    if not bon_id.empty:
        results = []
        for _, row in bon_id.iterrows():
            results.append({
                "id": int(row['id']),
                "nom": row['nom'],
                "date": row['date'],
                "lieu": row['lieu'],
                "description": row['description']
            })
        return results, 200
    return { "error": "Association not found" }, 404


# ## Liste des associations par type

# * Endpoint : `/api/associations/type/<type>`
# * Méthode : GET
# * Description : Retourne une liste des associations par type (BDE, BDS, BDA, etc.).
# * Réponse :
#   + 200 OK : Liste des associations filtrées par type.
# * Note: cet endpoint n'est pas testé par le frontend pour le moment.

@app.route('/api/associations/type/<type>', methods=['GET'])
def get_associations_by_type(type):
    result = []
    bon_type = associations_df[associations_df['type'] == type]
    for _, row in bon_type.iterrows():
        result.append({
            "id": int(row['id']),
            "nom": row['nom'],
            "type": row['type'],
            "description": row['description']
        })
    return result, 200


if __name__ == '__main__':
    app.run(debug=False)
