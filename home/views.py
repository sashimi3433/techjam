from django.shortcuts import render
from django.http import HttpResponse
from . import views


def index(request):
    return render(request, 'home/index.html')