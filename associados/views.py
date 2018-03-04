from django.shortcuts import render
from .models import Turma
from django.http import HttpResponse
import simplejson


# Create your views here.


def getvaloraula(request):
    if request.is_ajax():
        json = {}
        json['error'] = False
        if request.GET.get('turma'):
            turma = Turma.objects.get(pk=request.GET.get('turma'))
            json['valor_aula'] = turma.seminario.vl_hora_aula

        return HttpResponse(simplejson.dumps(json))
