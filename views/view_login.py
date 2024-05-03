from django.shortcuts import render, redirect
from django.http import HttpResponse

from sqlalchemy.exc import SQLAlchemyError
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_queries import *
from horizon_pricer.models.data.db.db_loading import *

from django.contrib.auth.forms import AuthenticationForm

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # Authentification réussie, rediriger vers la page d'accueil
            return redirect('view_home')
    else:
        form = AuthenticationForm()
    return render(request, 'template_login.jinja2', {'form': form})