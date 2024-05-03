from django.shortcuts import render
import pandas as pd

def my_view(request):
    # Chemin vers le fichier Excel
    excel_file_path = "horizon_pricer/models/data/mcl.xlsx"
    
    # Lire le fichier Excel
    data = pd.read_excel(excel_file_path)
    
    # Convertir les données en dictionnaire pour les passer au template
    data_dict = data.to_dict(orient='records')
    
    # Formater les dates au format jour/mois/année
    for item in data_dict:
        item['date_emission'] = item['date_emission'].strftime('%d/%m/%Y')
        item['date_jouissance'] = item['date_jouissance'].strftime('%d/%m/%Y')
        item['date_echeance'] = item['date_echeance'].strftime('%d/%m/%Y')
    
    # Passer les données au template pour les afficher
    return render(request, 'template_mcl.jinja2', {'data': data_dict})