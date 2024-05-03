from django.shortcuts import render, redirect
from sqlalchemy.exc import SQLAlchemyError
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_loading import *
from horizon_pricer.models.data.db.db_queries import *

from horizon_pricer.models.data.db.helpers.p_factory import *
from django import forms

import datefinder
from deform import Form, Button
from colander import MappingSchema, SchemaNode, Date
import deform, colander
import datetime as dt

dbs = dbsession()



def creer_portefeuille(request):
    if request.method == 'POST':
        # Si le formulaire est soumis
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        
        # Création d'un nouveau portefeuille avec SQLAlchemy
        nouveau_portefeuille = Portefeuille(nom=nom, description=description)
        dbs.add(nouveau_portefeuille)
        dbs.commit()

        return redirect('liste_portefeuilles')
    else:
        # Si la requête est GET, affichage du formulaire vide
        return render(request, 'creer_portefeuille.jinja2')

def liste_portefeuilles(request):
    # Récupération de la liste des portefeuilles avec SQLAlchemy
    portefeuilles = query_portefeuille(dbs)
    return render(request, 'liste_portefeuilles.jinja2', {'portefeuilles': portefeuilles})

def details_portefeuille(request, portefeuille_id):
    # Récupération des détails du portefeuille avec SQLAlchemy
    portefeuille = dbs.query(Portefeuille).filter_by(id=portefeuille_id).first()
    titres = query_titres(dbs, portefeuille_id)

    if request.method == 'POST':
        selected_titles = request.POST.getlist('select')
        quantities = request.POST.getlist('quantity')
        data_dict = request.POST.get('data_dict')  # Récupérer data_dict depuis le contexte

        for title, quantity in zip(selected_titles, quantities):
            nouveau_titre = Titre(
                portefeuille_id=portefeuille_id,
                code_isin=title,
                nom_emetteur=data_dict.loc[data_dict['code_isin'] == title, 'nom_emetteur'].iloc[0],
                famille_instrument=data_dict.loc[data_dict['code_isin'] == title, 'famille_instrument'].iloc[0],
                qt_emise=data_dict.loc[data_dict['code_isin'] == title, 'qt_emise'].iloc[0],
                qt_ajoute=quantity
            )
            dbs.add(nouveau_titre)

        dbs.commit()
        # Rediriger vers la même page après l'ajout
        return redirect('details_portefeuille', portefeuille_id=portefeuille_id)

    return render(request, 'details_portefeuille.jinja2', {'portefeuille': portefeuille, 'titres': titres})





def ajouter_titre(request, portefeuille_id):
    excel_file_path = "horizon_pricer/models/data/mcl.xlsx"
    data = pd.read_excel(excel_file_path)
    data_dict = data.to_dict(orient='records')

    if request.method == 'POST':
        selected_titles = request.POST.getlist('select')
        quantities = request.POST.getlist('quantity')

        for title, quantity in zip(selected_titles, quantities):
            nouveau_titre = Titre(
                portefeuille_id=portefeuille_id,
                code_isin=title,
                nom_emetteur=data_dict.loc[data_dict['code_isin'] == title, 'nom_emetteur'].iloc[0],
                famille_instrument=data_dict.loc[data_dict['code_isin'] == title, 'famille_instrument'].iloc[0],
                qt_emise=data_dict.loc[data_dict['code_isin'] == title, 'qt_emise'].iloc[0],
                qt_ajoute=quantity
            )
            dbs.add(nouveau_titre)

        dbs.commit()

        return redirect('details_portefeuille', portefeuille_id=portefeuille_id)
    else:
        portefeuille = dbs.query(Portefeuille).filter_by(id=portefeuille_id).first()
        titres = dbs.query(Titre).filter_by(portefeuille_id=portefeuille_id).all()
        
        # Passer les données de la base de données et le DataFrame 'data' à la template
        return render(request, 'ajouter_titre2.jinja2', {'portefeuille': portefeuille, 'titres': titres, 'data': data_dict})



