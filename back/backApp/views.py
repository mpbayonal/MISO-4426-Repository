# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from .models import *
from .serializers import *
from rest_framework import generics
from . import serializers
from django.http import HttpResponse, JsonResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly

import datetime
import os 
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

import base64


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class ListProyecto(generics.ListCreateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer



class DetailProyecto(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer


class ListDiseno(generics.ListCreateAPIView):
    queryset = Diseno.objects.all()
    serializer_class = DisenoSerializer

class DetailDiseno(generics.RetrieveUpdateDestroyAPIView):
    queryset = Diseno.objects.all()
    serializer_class = DisenoSerializer
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = (IsAuthenticatedOrReadOnly,)

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw





class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)


class LinksPageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'links.html', context=None)


class Customers(TemplateView):
    def getCust(request):
        name = 'liran'
        return HttpResponse('{ "name":"' + name + '", "age":31, "city":"New York" }')


@csrf_exempt
def get_proyectos_Url(request, urlLink):

    if request.method == 'GET':

        user = UserCustom.objects.get(url = urlLink)
        data = Proyecto.objects.filter(empresa_id= user.id)
        serializer = ProyectoSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def get_diseno_proyecto(request, proyecto_id):

    if request.method == 'GET':

        proyecto = Proyecto.objects.get(id = proyecto_id)
        data = Diseno.objects.filter(
            proyecto_id= proyecto.id).filter(
                estado="Disponible")  
        for diseno in data:
            with open(diseno.url_archivo, 'rb') as fi:
                encoded_string = base64.b64encode(image_file.read())
                print(encoded_string)
                diseno.imagen = encoded_string
        serializer = DisenoSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def get_diseno_proyecto_Sin_Detalles(request, proyecto_id):

    if request.method == 'GET':

        proyecto = Proyecto.objects.get(id = proyecto_id)
        data = Diseno.objects.filter(proyecto_id= proyecto.id)
        serializer = DisenoSinDetallesSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def get_url_email(request, pUsername):

    if request.method == 'GET':
        user = UserCustom.objects.get(username = pUsername)
        user.url = user.username + "" + str(user.id)
        user.save()
        serializer = UserCustomURLSerializer(user, many=False)
        return JsonResponse(serializer.data, safe=False)




@csrf_exempt
def send_diseno(request):

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        input_image = files['image']
        proyecto = Proyecto.objects.get(id = data['proyecto'])
        # file_name = "{0}/{1}.{2}".format(str(proyecto.nombre), input_image.name,get_file_extension(input_image.name))
        file_name = "{0}".format(input_image.name)
        print(file_name)
        nuevoDiseño = Diseno(
            nombre=data['nombre'],
            apellido=data['apellido'],
            email=data['email'],
            estado=data['estado'],
            fecha=data['fecha'],
            pago=data['pago'],
            proyecto=proyecto,
            url_archivo=file_name
        )
        nuevoDiseño.save()
        with open(file_name, 'wb+') as destination:
            for chunk in input_image.chunks():
                destination.write(chunk)
        serializer = DisenoSerializer(nuevoDiseño, many=False)
        return JsonResponse(serializer.data, safe=False)

def allowed_file(filename):
    return '.' in filename and \
           get_file_extension(filename) in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def get_content_encoding(filename):
    return 'image/jpeg' if get_file_extension(filename) in ['jpg', 'jpeg'] else 'image/png'