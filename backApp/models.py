# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import boto3
from decimal import Decimal
from functools import partial

from django.contrib.auth.models import AbstractUser
from boto3.dynamodb.conditions import Key, Attr
from django.db import models
from django.conf import settings
import datetime


# Create your models here.
dynamodb = boto3.resource(
        'dynamodb',
        region_name='us-east-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )


class DynamoDBMapperMixin(object):
    """
    Mixin that maps a schema to DynamoDB
    """

    # This schema should be filled on the models using this mixin
    DYNAMO_DB_TABLE = None
    DYNAMO_DB_FIELDS = []

    def _get_dynamo_item(self, **kwargs):
        """
        Gets the item from DynamoDB
        Id in DynamoDB will be the same id as in Django model
        """
        try:
            self._cached_dynamodb_item = self._cached_dynamodb_item or \
                                         self.dynamodb_table.get_item(Key={'id': str(self.id)}, **kwargs)['Item']
            return self._cached_dynamodb_item
        except KeyError:
            if self.dynamodb_table.put_item(Item={'id': str(self.id)}):
                return self._get_dynamo_item(**kwargs)

    def _get_dynamo_field_value(self, field):
        try:
            return self._get_dynamo_item()[field]
        except KeyError:
            return None

    def _update_dynamo_field_value(self, field, value):
        # Cast digits to Decimal
        if type(value) in (int, float):
            value = Decimal(value)

        self._dynamodb_update_actions[field] = {'Value': value, 'Action': 'PUT'}
        setattr(self, '_' + field, value)  # Sets a cached value for the current instance

    def _delete_dynamo_field_value(self, field):
        self._dynamodb_update_actions[field] = {'Action': 'DELETE'}
        setattr(self, '_' + field, None)  # Sets a cached value for the current instance

    def clear_dynamodb_local_cache(self):
        for field in self.DYNAMO_DB_FIELDS:
            if hasattr(self, '_' + field):
                delattr(self, '_' + field)
        self._dynamodb_update_actions = {}
        self._cached_dynamodb_item = {}

    def __getattr__(self, name):
        if name in self.DYNAMO_DB_FIELDS:
            if hasattr(self, '_' + name):
                return getattr(self, '_' + name)
            else:
                return self._dynamodb_getters[name]()
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name in self.DYNAMO_DB_FIELDS:
            return self._dynamodb_setters[name](value=value)
        else:
            return super(DynamoDBMapperMixin, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.DYNAMO_DB_FIELDS:
            return self._dynamodb_deleters[name]()
        else:
            return super(DynamoDBMapperMixin, self).__delattr__(name)

    def __dir__(self):
        """
        Overrides __dir__ for autocompletion!
        """
        return super(DynamoDBMapperMixin, self).__dir__() + self.DYNAMO_DB_FIELDS

    def __init__(self, *args, **kwargs):
        # Get DynamoDB table instance
        self.dynamodb_table = dynamodb.Table(self.DYNAMO_DB_TABLE)

        # Cached dynamodb item
        self._cached_dynamodb_item = {}

        # Update actions storage: Actions will be performed on save() call
        self._dynamodb_update_actions = {}

        # Store getters & setters
        self._dynamodb_getters = {}
        self._dynamodb_setters = {}
        self._dynamodb_deleters = {}

        # Create getters & setters for Dynamo DB fields
        for field in self.DYNAMO_DB_FIELDS:
            self._dynamodb_getters[field] = partial(self._get_dynamo_field_value, field=field)
            self._dynamodb_setters[field] = partial(self._update_dynamo_field_value, field=field)
            self._dynamodb_deleters[field] = partial(self._delete_dynamo_field_value, field=field)

        return super(DynamoDBMapperMixin, self).__init__(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.dynamodb_table.delete_item(Key={'id': str(self.id)})
        return super(DynamoDBMapperMixin, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(DynamoDBMapperMixin, self).save(*args, **kwargs)

        # Perform update item in dynamodb if needed
        if self._dynamodb_update_actions:
            self.dynamodb_table.update_item(
                Key={'id': self.id},
                AttributeUpdates=self._dynamodb_update_actions,
            )
            self.clear_dynamodb_local_cache()


class UserCustom(DynamoDBMapperMixin, AbstractUser):

    url = models.CharField(max_length=500, default= "url")

    DYNAMO_DB_TABLE = 'designmatch-usuarios'
    table = dynamodb.Table(DYNAMO_DB_TABLE)

    DYNAMO_DB_FIELDS = [
        'Username',  'Password', 'Url', 'id', 'Email']

    @classmethod
    def get_id(cls, id):
        return cls.table.query(
            KeyConditionExpression=Key('id').eq(id))

    @classmethod
    def get_email(cls, email):
        return cls.table.query(
            KeyConditionExpression=Key('email').eq(email)
        )

    def save(self, *args, **kwargs):

        idFinal = str(uuid.uuid4())
        urlFinal = self.Username +  idFinal
        self.table.put_item(
            Item={
                'username': self.Username,
                'password': self.Password,
                'email': self.Email,
                'url': urlFinal,
                'id': idFinal
            }
        )


    # add additional fields in here


# class Empresa(models.Model):
#
#
#     url = models.CharField(max_length=500)
#
#     def __str__(self):
#         return self.nombre







class Proyecto(DynamoDBMapperMixin, models.Model):

    DYNAMO_DB_TABLE = 'designmatch-proyectos'
    table = dynamodb.Table(DYNAMO_DB_TABLE)
    DYNAMO_DB_FIELDS = [
        'empresa', 'nombre', 'descripcion', 'pago'
    ]

    empresa = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=500)
    descripcion = models.CharField(max_length=500)
    pago = models.IntegerField()

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.table.put_item(
            Item={
                'empresa': self.empresa,
                'nombre': self.nombre,
                'descripcion': self.descripcion,
                'pago': self.pago
            }
        )


class Diseno(DynamoDBMapperMixin, models.Model):

    DYNAMO_DB_TABLE = 'designmatch-disenos'
    table = dynamodb.Table(DYNAMO_DB_TABLE)
    DYNAMO_DB_FIELDS = [
        'nombre', 'apellido', 'email', 'estado', 'fecha', 'pago','archivo', 'url_archivo_modificado', 'proyecto'
    ]

    nombre = models.CharField(max_length=500)
    apellido = models.CharField(max_length=500)
    email = models.CharField(max_length=500)
    estado = models.CharField(max_length=500)
    fecha = models.DateTimeField(default=datetime.datetime.utcnow)
    pago = models.IntegerField()
    archivo = models.ImageField(upload_to='noProcesadas')
    url_archivo_modificado = models.ImageField(upload_to='disponibles', null=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.table.put_item(
            Item={
                'apellido': self.apellido,
                'nombre': self.nombre,
                'email': self.email,
                'fecha': self.fecha
            }
        )








