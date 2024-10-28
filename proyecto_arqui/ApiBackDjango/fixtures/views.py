from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.http import JsonResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from .models import Fixture, Bonos, User, Recommendation
from .serializers import FixtureSerializer, BonosSerializer, UserSerializer, RecommendationSerializer
from django.utils import timezone
import json
from datetime import datetime
import requests
import paho.mqtt.publish as publish
import json
import uuid6
import requests


from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes







# Configuración del broker MQTT
MQTT_HOST = 'broker.iic2173.org'  # Dirección del broker
MQTT_PORT = 9000                  # Puerto del broker
MQTT_USER = 'students'            # Usuario
MQTT_PASSWORD = 'iic2173-2024-2-students'  # Contraseña

#tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))



# /users
class UserView(APIView):
    """
    Vista para manejar la creación de usuarios (POST) y listar todos los usuarios (GET).
    """

    # GET: Obtener la lista de todos los usuarios
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # POST: Crear un nuevo usuario
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# /users/<user_id>
class UserDetailView(APIView):
    """
    Vista para obtener (GET), actualizar (PUT), o borrar (DELETE) un usuario específico.
    """

    def get_object(self, user_id):
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise Http404

    # GET: Obtener un usuario específico por su user_id
    def get(self, request, user_id, *args, **kwargs):
        user = self.get_object(user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # PUT: Actualizar un usuario específico
    def put(self, request, user_id, *args, **kwargs):
        user = self.get_object(user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Borrar un usuario específico
    def delete(self, request, user_id, *args, **kwargs):
        user = self.get_object(user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class addwallet(APIView):

    def patch(self,request, **kwargs):
        request_data = request.data
        user_id = request_data.get('user')
        money_to_add = request_data.get('quantity')
       # Validar que se proporcionen user_id y cantidad