import base64
import os
import bcrypt
import jwt
import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.core import serializers
from django.utils.crypto import get_random_string
from rest_framework.utils import json

from . import serializers
from .models import *
from .serializers import *
from .tasks import process_image_and_send_mail

from boto3 import resource, client
from botocore.exceptions import ClientError

'''
path('proyecto/<urlLink>/', views.get_proyectos_Url),
path('user/<pUsername>/', views.get_url_email),
path('disenos/<int:proyecto_id>/', views.get_diseno_proyecto),

path('proyectos/', views.ListProyecto.as_view()),
path('proyectos/<int:pk>/', views.DetailProyecto.as_view()),

path('diseno/<int:pk>/', views.getDisenoById),
path('diseno/', views.send_diseno),
path('proyectos/<int:id_empresa>/crear/', views.send_proyecto),

path('auth/', include('rest_auth.urls')),
path('auth/signup/', include('rest_auth.registration.urls')),
'''

s3_images_bucket = 'designmatch-grupo2'
@csrf_exempt
def getDisenoById(request, pk):
    if request.method == 'GET':

        diseno = Diseno.get_id(pk)

        print(diseno)
        if diseno['Count'] < 1:
            return HttpResponse(status=404)

        else:
            return HttpResponse(diseno['Items'][0])

#     path('proyectos/<pk>/', views.getProyectoById),


@csrf_exempt
def getProyectoById(request, pk):
    if request.method == 'GET':
        proyecto = Proyecto.get_id(pk)

        if proyecto['Count'] < 1:
            return HttpResponse(status=404)

        else:
            return HttpResponse(proyecto['Items'])


#     path('proyectos/<pk>/editar/', views.editar_proyecto),
@csrf_exempt
def editar_proyecto(request, pk):

    if request.method == 'POST':

        proyecto = Proyecto.get_id(pk)

        if proyecto['Count'] < 1:
            return HttpResponse(status=404)

        else:
            data = request
            body_unicode = request.body.decode('utf-8')

            body = json.loads(body_unicode)
            nombre = body['nombre']
            pago = body['pago']
            descripcion = body['descripcion']
            empresa = body['empresa']
            proyecto = Proyecto.update(descripcion, nombre, pago, pk, empresa)

            data = serializers.serialize("json", proyecto)

            return HttpResponse(data)


#     path('proyectos/<int:pk>/eliminar/', views.eliminar_proyecto),
@csrf_exempt
def eliminar_proyecto(request, pk):

    if request.method == 'POST':

        proyecto = Proyecto.get_id(pk)

        if proyecto['Count'] < 1:
            return HttpResponse(status=404)

        else:
            Proyecto.delete(pk)

            return HttpResponse(status=204)


# path('proyecto/<urlLink>/', views.get_proyectos_Url),
@csrf_exempt
def get_proyectos_Url(request, urlLink):

    if request.method == 'GET':

        user = UserCustom.get_url(urlLink)

        if user['Count'] < 1:
            return HttpResponse(status=404)

        else:
            id_Empresa = user['Items'][0]['id']
            print(id_Empresa)
            proyectos = Proyecto.get_idEmpresa(id_Empresa)['Items']

            return HttpResponse(proyectos)


#     path('disenos/<int:proyecto_id>/', views.get_diseno_proyecto),
@csrf_exempt
def get_diseno_proyecto(request, proyecto_id):

    if request.method == 'GET':

        proyecto = Proyecto.get_id(proyecto_id)
        if proyecto['Count'] < 1:
            return HttpResponse(status=404)

        else:
            disenos = Diseno.get_diseno_proyecto(proyecto_id)
            print(disenos)
            return HttpResponse(disenos['Items'])


#     path('user/<pEmail>/', views.get_url_email),
@csrf_exempt
def get_urlEmpresa_email(request, pEmail):

    if request.method == 'GET':
        empresa = UserCustom.get_email(pEmail)

        print(empresa)
        if empresa['Count'] < 1:
            return HttpResponse(status=404)

        else:
            return HttpResponse(empresa['Items'])


def save_diseno(data, image, name):
    nuevoDiseño = Diseno()
    nuevoDiseño.nombre = data['nombre']
    nuevoDiseño.apellido = data['apellido']
    nuevoDiseño.email = data['email']
    nuevoDiseño.estado = data['estado']
    nuevoDiseño.pago = data['pago']
    nuevoDiseño.proyecto = data['proyecto']
    nuevoDiseño.archivo = name
    resource('s3').Bucket(s3_images_bucket).put_object(
        Body=image,
        Key=name
    )
    nuevoDiseño.save()
    return nuevoDiseño

#     path('diseno/', views.send_diseno),
@csrf_exempt
def send_diseno(request):

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        input_image = files['image']

        proyecto = Proyecto.get_id(data['proyecto'])

        if proyecto['Count'] < 1:
            return HttpResponse(status=404)
        else:
            # https://designmatch-grupo2.s3.amazonaws.com/noProcesado/ffvii-remake-aerith-gold-saucer.jpg
            diseno = {}
            try:
                file_object = resource('s3').Object(
                    s3_images_bucket, 'noProcesado/'+input_image.name).last_modified
                dir_name, file_name = os.path.split(input_image.name)
                file_root, file_ext = os.path.splitext(file_name)
                new_name = '{0}{1}{2}{3}'.format(
                    file_root, '_', get_random_string(), file_ext)
                diseno = save_diseno(
                    data, input_image, 'noProcesado/'+new_name)
            except ClientError:
                diseno = save_diseno(
                    data, input_image, 'noProcesado/'+input_image.name)
            send_task(diseno.id)
            return HttpResponse(
                json.dumps(dict(
                    id=diseno.id,
                    nombre=diseno.nombre,
                    apellido=diseno.apellido,
                    archivo=diseno.archivo,
                    email=diseno.email,
                    fecha=str(diseno.fecha),
                    url_archivo=diseno.url_archivo,
                    pago=diseno.pago,
                    estado=diseno.estado
                ))
            )


def send_task(diseno):
    sqs = client('sqs', 'us-east-1')
    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/547712166517/designmatch-d', 
        MessageBody=diseno)


#     path('proyectos/<int:id_empresa>/crear/', views.send_proyecto),
@csrf_exempt
def send_proyecto(request, email_empresa):

    if request.method == 'POST':
        data = request
        body_unicode = request.body.decode('utf-8')
        empresa = UserCustom.get_email(email_empresa)
        print(empresa)
        body = json.loads(body_unicode)
        print(body)

        if empresa['Count'] < 1:
            return HttpResponse(status=404)

        else:
            id_Empresa = empresa['Items'][0]['id']
            nuevoProyecto = Proyecto(
            )
            nuevoProyecto.nombre = body['nombre']
            nuevoProyecto.empresa = id_Empresa
            nuevoProyecto.pago = body['pago']
            nuevoProyecto.descripcion = body['descripcion']

            nuevoProyecto.save()
            data = serializers.serialize("json", nuevoProyecto)
            print(nuevoProyecto)

            return HttpResponse(data)

# path('auth/signup/', views.registro),
@csrf_exempt
def registro(request):

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')

        body = json.loads(body_unicode)
        empresa = UserCustom.get_email(body['email'])
        print(empresa)

        print(empresa['Count'] > 0)
        if empresa['Count'] > 0:
            return HttpResponse(status=409)

        if body['password2'] != body['password1']:
            return HttpResponse(status=401)

        else:
            password = body['password1']
            b = password.encode('utf-8')  # I just added this line
            password_encrypt = bcrypt.hashpw(b, bcrypt.gensalt())

            empresa2 = UserCustom()
            empresa2.username = body['username']
            empresa2.password = password_encrypt
            empresa2.email = body['email']
            empresa2.save()

            data = serializers.serialize("json", empresa2)
            print(data)
            return HttpResponse(data)

#path('auth/', views.login),
@csrf_exempt
def login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')

        body = json.loads(body_unicode)
        empresa = UserCustom.get_email(body['email'])

        if empresa['Count'] < 1:
            return HttpResponse(status=404)

        password = body['password'].encode('utf-8')

        passwordHash = empresa['Items'][0]['password'].value

        if bcrypt.checkpw(password, passwordHash) == False:
            return HttpResponse(status=401)

        else:

            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=900),
                'iat': datetime.datetime.utcnow(),
                'sub': empresa['Items'][0]['id']
            }
            token = jwt.encode(
                payload,
                settings.SECRET_KEY,
                algorithm='HS256'
            )

            #payload = jwt.decode(auth_token, settings.SECRET_KEY)

            UserCustom.update(empresa['Items'][0]['email'], 'token', token)

            print(empresa)

            return HttpResponse(empresa['Items'])