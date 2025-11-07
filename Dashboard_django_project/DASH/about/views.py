# about/views.py
from django.shortcuts import render

def como_funciona(request):
    return render(request, 'about/como_funciona.html')

def sobre_nosotros(request):
    return render(request, 'about/sobre_nosotros.html')