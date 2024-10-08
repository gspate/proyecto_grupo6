from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.http import Http404
from .models import Fixture, Bonos, User
from .serializers import FixtureSerializer, UserSerializer
from django.utils.timezone import now
from datetime import datetime
import json
import paho.mqtt.publish as publish
import time
import uuid6

# Configuración del broker MQTT
MQTT_HOST = 'broker.iic2173.org'  # Dirección del broker
MQTT_PORT = 9000                  # Puerto del broker
MQTT_USER = 'students'            # Usuario
MQTT_PASSWORD = 'iic2173-2024-2-students'  # Contraseña


class UserView(APIView):
    """
    Vista para manejar la creación de usuarios (POST) y listar todos los usuarios (GET).
    """

    # # GET: Obtener la lista de todos los usuarios
    # def get(self, request, *args, **kwargs):
    #     users = User.objects.all()
    #     serializer = UserSerializer(users, many=True)
    #     return Response(serializer.data)

    # POST: Crear un nuevo usuario
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


# Vista para listar y filtrar fixtures (partidos)
class FixtureList(APIView):
    """
    Vista para listar y crear partidos (fixtures).
    """

    # Manejar GET (obtener lista de fixtures)
    def get(self, request, *args, **kwargs):
        # Filtrar solo partidos futuros
        queryset = Fixture.objects.filter(date__gte=now())
        
        # Obtener parámetros de consulta opcionales
        home_team = request.query_params.get('home')
        away_team = request.query_params.get('away')
        date = request.query_params.get('date')

        # Aplicar filtros si se proporcionan
        if home_team:
            queryset = queryset.filter(home_team_name__icontains=home_team)
        if away_team:
            queryset = queryset.filter(away_team_name__icontains=away_team)
        if date:
            queryset = queryset.filter(date__date=date)
        
        # Serializar los datos
        serializer = FixtureSerializer(queryset, many=True)
        
        return Response(serializer.data)

    # Manejar POST (crear un nuevo fixture)
    def post(self, request, *args, **kwargs):
        serializer = FixtureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FixtureDetail(APIView):
    """
    Vista para obtener (GET) o actualizar (PUT) un fixture específico.
    """
    def get_object(self, fixture_id):
        try:
            return Fixture.objects.get(fixture_id=fixture_id)
        except Fixture.DoesNotExist:
            raise Http404

    # Manejar GET (obtener un fixture por fixture_id)
    def get(self, request, fixture_id, *args, **kwargs):
        fixture = self.get_object(fixture_id)
        serializer = FixtureSerializer(fixture)
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        fixture = self.get_object(kwargs.get('fixture_id'))
        serializer = FixtureSerializer(fixture, data=request.data)  # Asocia el fixture existente
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BonosView(APIView):
    def post(self, request, *args, **kwargs):
        request_data = request.data
        fixture_id_request = request_data.get('fixture_id')
        user_id = request_data.get('user_id')  # Asumiendo que se pasa el user_id en la request
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos solicitados
        cost_per_bonus = 1000  # Precio por cada bono

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Calcular el costo total de los bonos
        total_cost = cost_per_bonus * quantity

        # Validar si el usuario tiene suficiente dinero en su billetera
        if user.wallet < total_cost:
            return Response({"error": "Fondos insuficientes"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar si hay suficientes bonos disponibles
        if fixture.available_bonuses >= quantity:
            # Descontar el dinero de la billetera del usuario
            user.wallet -= total_cost
            user.save()

            # Descontar temporalmente los bonos disponibles
            fixture.available_bonuses -= quantity
            fixture.save()

            # Generar un UUIDv6 para el request_id
            request_id = uuid6.uuid6()  # Esto mantiene el UUIDv6

            # Crear la solicitud de bono
            bonus_request = Bonos.objects.create(
                request_id=request_id,  # Mantener UUIDv6 aquí
                fixture=fixture,
                user=user,  # Asocia el bono con el usuario
                quantity=quantity,
                group_id=request_data.get('group_id'),
                league_name=request_data.get('league_name'),
                round=request_data.get('round'),
                date=timezone.now(),
                result=request_data.get('result', '---'),
                seller=request_data.get('seller', 0)
            )

            # Publicar los datos en MQTT
            data = {
                "request_id": str(bonus_request.request_id),  # Convertir UUIDv6 a string
                "fixture": fixture.fixture_id,
                "quantity": quantity,
                "group_id": request_data.get('group_id'),
                "league_name": request_data.get('league_name'),
                "round": request_data.get('round'),
                "date": timezone.now(),
                "result": request_data.get('result', '---'),
                "seller": request_data.get('seller', 0)
            }

            # Convertir el diccionario a una cadena JSON
            json_data = json.dumps(data)

            publish.single(
                topic='fixtures/request',
                payload=json_data,
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                auth={'username': MQTT_USER, 'password': MQTT_PASSWORD}
            )

            return Response({
                "request_id": str(bonus_request.request_id),  # Asegúrate de que el UUIDv6 se devuelva como string
                "message": "Bonos comprados y dinero descontado exitosamente"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No hay suficientes bonos disponibles"}, status=status.HTTP_400_BAD_REQUEST)


class BonusRequestView(APIView):
    """
    Vista para almacenar solicitudes de compra de bonos desde el canal fixtures/requests.
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data
        fixture_id_request = request_data.get('fixture_id')
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos solicitados

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Extraer y formatear la fecha
        raw_date = request_data.get('date')
        try:
            # Convertir la fecha de "YYYY-MM-DDThh:mm:ssZ" a "YYYY-MM-DD"
            formatted_date = datetime.strptime(raw_date[:10], '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # Validar si hay suficientes bonos disponibles
        if fixture.available_bonuses >= quantity:
            # Descontar temporalmente los bonos
            fixture.available_bonuses -= quantity
            fixture.save()

            # Crear una nueva solicitud de bono (BonusRequest)
            bonus_request = Bonos.objects.create(
                request_id=request_data.get('request_id'),
                fixture=fixture,
                quantity=quantity,
                group_id=request_data.get('group_id'),
                league_name=request_data.get('league_name'),
                round=request_data.get('round'),
                date=formatted_date,  # Fecha corregida
                result=request_data.get('result', '---'),
                seller=request_data.get('seller', 0),
                datetime=request_data.get('datetime')  # Usar el datetime que ya viene en el payload
            )

            return Response({
                "request_id": bonus_request.request_id,
                "message": "Bonos reservados temporalmente"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No hay suficientes bonos disponibles"}, status=status.HTTP_400_BAD_REQUEST)



class BonusValidationView(APIView):
    """
    Vista para procesar validaciones de solicitudes de bonos desde el canal fixtures/validation.
    """
    def put(self, request, request_id, *args, **kwargs):
        # Extraer la validación y el request_id
        validation_data = request.data

        # Verificar que tenemos el campo valid
        valid = validation_data.get('valid', None)
        if valid is None:
            return Response({"error": "El campo 'valid' no fue encontrado en los datos de validación"}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la solicitud de bonos
        try:
            bonus_request = Bonos.objects.get(request_id=request_id)
        except Bonos.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Procesar la validación
        if valid:
            bonus_request.status = 'approved'
            bonus_request.save()

            return Response({
                "message": f"Compra con request_id {request_id} aprobada."
            }, status=status.HTTP_200_OK)
        else:
            # Si no es válida, devolver los bonos al fixture
            fixture = bonus_request.fixture
            fixture.available_bonuses += bonus_request.quantity
            fixture.save()

            bonus_request.status = 'rejected'
            bonus_request.save()

            return Response({
                "message": f"Compra con request_id {request_id} rechazada. Bonos devueltos."
            }, status=status.HTTP_400_BAD_REQUEST)
