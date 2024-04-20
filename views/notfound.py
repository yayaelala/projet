from django.shortcuts import render

def notfound_view(request):
    context = {}
    return render(request, '404.jinja2', context, status=404)