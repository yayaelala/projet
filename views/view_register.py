from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def my_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Rediriger vers la page de login après l'inscription réussie
            return redirect('view_login')
    else:
        form = UserCreationForm()
    return render(request, 'template_register.jinja2', {'form': form})
