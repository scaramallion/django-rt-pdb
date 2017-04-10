from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return HttpResponse('THIS IS A TEST')

def do_machine(request):
    return HttpResponse('')

def do_beam(request):
    return HttpResponse('')

def get_data(request):
    return HttpResponse('')

def interpolate_wrapper(request):
    return HttpResponse('')
