from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from .models import Fixture, Bonos, User
from .serializers import FixtureSerializer, BonosSerializer, UserSerializer
from datetime import datetime
import paho.mqtt.publish as publish
import json
import time
import uuid6
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.webpay.webpay_plus.integration_commerce_codes import IntegrationCommerceCodes
from transbank.webpay.webpay_plus.integration_api_keys import IntegrationApiKeys


# Configuración del broker MQTT
MQTT_HOST = 'broker.iic2173.org'  # Dirección del broker
MQTT_PORT = 9000                  # Puerto del broker
MQTT_USER = 'students'            # Usuario
MQTT_PASSWORD = 'iic2173-2024-2-students'  # Contraseña

tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))



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

# /fixtures
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

# /fixtures/<fixture_id>
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

# bonos
# Esta vista esta en desarrollo, no esta terminada

class AskTransbank(APIView):
    pass
class BonosView(APIView):

    # GET: Obtener la lista de todos los usuarios
    def get(self, request, *args, **kwargs):
        bonos = Bonos.objects.all()
        serializer = BonosSerializer(bonos, many=True)
        return Response(serializer.data)

    # POST: compra de bono
    def post(self, request, *args, **kwargs):
        request_data = request.data
        fixture_id_request = request_data.get('fixture_id')
        user_id = request_data.get('user_id')  # Asumiendo que se pasa el user_id en la request
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos solicitados
        cost_per_bonus = 1000  # Precio por cada bono
        method = request_data.get('wallet')
        for_who = request_data.get('for')

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)


        total_cost = cost_per_bonus * quantity

        if method:
            # Validar si el usuario tiene suficiente dinero en su billetera
            if user.wallet < total_cost:
                return Response({"error": "Fondos insuficientes"}, status=status.HTTP_400_BAD_REQUEST)

            # Descontar el dinero de la billetera del usuario
            user.wallet -= total_cost
            user.save()

        else:
            #### webpay
            pass
        
        # Validar si hay suficientes bonos disponibles
        if fixture.available_bonuses >= quantity:
            # Descontar temporalmente los bonos disponibles
            fixture.available_bonuses -= quantity
            fixture.save()

            # Generar un UUIDv6 para el request_id
            try:

                request_id = uuid6.uuid6()

            except:
                return Response ({"error": "uuid6 failed"}, status=status.HTTP_400_BAD_REQUEST)

            # Crear la solicitud de bono
            bonus_request = Bonos.objects.create(
                request_id=request_id,
                fixture_id=fixture,
                user=user,
                quantity=quantity,
                group_id=request_data.get('group_id'),
                league_name=request_data.get('league_name'),
                round=request_data.get('round'),
                date=datetime.now(),
                result=request_data.get('result', '---'),
                seller=request_data.get('seller', 0),
                wallet=request_data.get('wallet'),
                for_who=request_data.get("for_who"),

            )
            token = 0### deposit token
            # Publicar los datos en MQTT
            data = {
                "request_id": str(bonus_request.request_id),
                "group_id": request_data.get('group_id'),
                "fixture_id": fixture.fixture_id,
                "league_name": request_data.get('league_name'),
                "round": request_data.get('round'),
                "date": request_data.get('date'),
                "result": request_data.get('result', '---'),
                "depostit_token": f"{token}",
                "datetime": datetime.now(),
                "quantity": quantity,
                "wallet": request_data.get('wallet'),
                "seller": request_data.get('seller', 0),
                
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
                "method": method,
                "request_id": str(bonus_request.request_id),
                "message": "Bonos comprados exitosamente"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No hay suficientes bonos disponibles"}, status=status.HTTP_400_BAD_REQUEST)
        

# mqtt/requests
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
                wallet=request_data.get('wallet'),
                datetime=request_data.get('datetime')  # Usar el datetime que ya viene en el payload
            )

            return Response({
                "request_id": bonus_request.request_id,
                "message": "Bonos reservados temporalmente"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No hay suficientes bonos disponibles"}, status=status.HTTP_400_BAD_REQUEST)


# mqtt/validations
# Esta vista debe ser actualizada para devolver el dinero gastado al usuario en caso de que una solicitud sea rechazada.
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

            return Response({
                "message": f"Compra con request_id {request_id} aprobada."
            }, status=status.HTTP_200_OK)
        else:
            # Si no es válida, devolver los bonos al fixture
            fixture = bonus_request.fixture
            fixture.available_bonuses += bonus_request.quantity
            fixture.save()

            return Response({
                "message": f"Compra con request_id {request_id} rechazada. Bonos devueltos."
            }, status=status.HTTP_400_BAD_REQUEST)

# mqtt/history
class BonusHistoryView(APIView):

    def post(self, request, *args, **kwargs):
        # Paso 1: Obtener y decodificar el JSON del request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=400)

        fixtures = data.get('fixtures', [])
        if not fixtures:
            return JsonResponse({"error": "No fixtures found in the request"}, status=400)

        fixtures_not_found = []
        fixtures_processed = 0  # Contador de fixtures procesados

        for fixture_data in fixtures:
            fixture_info = fixture_data.get('fixture')
            goals_info = fixture_data.get('goals')  # Corregido: goals está dentro de fixture

            # Paso 2: Buscar si la fixture existe en la base de datos
            try:
                fixture = Fixture.objects.get(fixture_id=fixture_info['id'])
            except Fixture.DoesNotExist:
                fixtures_not_found.append(fixture_info['id'])
                continue
            except Exception as e:
                return JsonResponse({"error": f"Error al buscar fixture: {str(e)}"}, status=500)

            # Determinar el ganador
            try:
                home_goals = goals_info.get('home', 0)
                away_goals = goals_info.get('away', 0)

                # Paso 3: Determinar el ganador
                if home_goals is not None and away_goals is not None:
                    if home_goals > away_goals:
                        match_result = 'home'
                        odds_value = fixture.odds_home_value
                    elif away_goals > home_goals:
                        match_result = 'away'
                        odds_value = fixture.odds_away_value
                    else:
                        match_result = 'draw'
                        odds_value = fixture.odds_draw_value

                    if not odds_value:
                        continue  # Si no hay odds, saltamos esta fixture
                else:
                    continue  # Saltar si los goles son None
            except Exception as e:
                return JsonResponse({"error": f"Error al determinar el resultado del partido: {str(e)}, {fixture_info},"}, status=500)

            # Incrementar el contador de fixtures procesados
            fixtures_processed += 1

            # Paso 4: Buscar todos los bonos relacionados con la fixture
            try:
                bonos = Bonos.objects.filter(fixture=fixture).select_related('user')

                for bono in bonos:
                    # Paso 5: Verificar si el bono ya fue procesado
                    if bono.status != 'pendiente':
                        continue

                    # Validar si el resultado del bono coincide con el del partido
                    if bono.result == match_result:
                        amount_to_credit = bono.quantity * 1000 * odds_value
                        user = bono.user
                        if user:
                            user.wallet += amount_to_credit
                            user.save()
                            bono.status = 'ganado'
                            bono.save()
                        else:
                            bono.status = 'perdido'
                            bono.save()
                    else:
                        bono.status = 'perdido'
                        bono.save()

            except Exception as e:
                return JsonResponse({"error": f"Error al procesar bonos: {str(e)}"}, status=500)

        # Paso final: devolver una respuesta de éxito
        total_fixtures = len(fixtures)
        return JsonResponse({
            "status": "success",
            "message": "Bonos procesados correctamente",
            "fixtures_not_found": fixtures_not_found,
            "fixtures_processed": fixtures_processed,
            "total_fixtures": total_fixtures
        })
