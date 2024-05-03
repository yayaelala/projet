from django.shortcuts import render
import pandas as pd
from horizon_pricer.models.pricer.module_pricing import *

def extract_obligation_parameters(isin):
    excel_file_path = "myapp/models/data/mcl.xlsx"
    data = pd.read_excel(excel_file_path)
    obligation = data[data['code_isin'] == isin]
    if obligation.empty:
        return None  # ISIN non valide
    obligation_dict = obligation.iloc[0].to_dict()
    return obligation_dict

def get_liste_isin():
    excel_file_path = "myapp/models/data/mcl.xlsx"
    data = pd.read_excel(excel_file_path)
    return data['code_isin'].tolist()

def my_view(request, template_name='template_pricer.jinja2'):
    if request.method == 'POST':
        isin = request.POST.get('isin')
        obligation_params = extract_obligation_parameters(isin)
        if obligation_params:
            context = {'obligation': obligation_params}
            return render(request, template_name, context)
        else:
            erreur = "ISIN invalide, veuillez entrer un code ISIN valide."
            return render(request, template_name, {'erreur': erreur})
    else:
        liste_isin = get_liste_isin()
        return render(request, template_name, {'liste_isin': liste_isin})