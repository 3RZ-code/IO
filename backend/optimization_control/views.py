from django.shortcuts import render
from .utils import run_my_code

def index(request):
    result = run_my_code('')
    return render(request, 'optimization_control/run.html', {'result': result})