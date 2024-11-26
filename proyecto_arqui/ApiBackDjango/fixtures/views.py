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
from django.db.models import Sum
from .models import Fixture, Bonos, User, Recommendation, Auctions
from .serializers import FixtureSerializer, BonosSerializer, UserSerializer, RecommendationSerializer, AuctionsSerializer
from django.utils import timezone
import json
from datetime import datetime
import requests
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import uuid6
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Configuración del broker MQTT
MQTT_HOST = "broker.iic2173.org"
MQTT_PORT = 9000
MQTT_TOPIC = "fixtures/requests"
MQTT_AUC = "fixtures/auctions"
MQTT_USER = "students"
MQTT_PASSWORD = "iic2173-2024-2-students"

LAMBDA_URL = 'https://nfu5ofywqc.execute-api.us-east-1.amazonaws.com/dev/pdf'

#tx = Transaction(WebpayOptions(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY, IntegrationType.TEST))

# Función para hacer las llamadas a Lambda (generar boletas) y enviarlas al correo del usuario
def GenerateAndSendPdfToUserEmail(fixture, user):
    payload = {
        "groupName": "Grupo 6",
        "userName": user.username,
        "teamsInfo": [fixture.home_team_name, fixture.away_team_name],
    }

    try:
        result = requests.post(LAMBDA_URL, json=payload)
        if result.status_code == 200:
            print("PDF generado exitosamente")
            pdf_link = result.json().get("url")
            try:
                send_email_with_pdf_link(pdf_link, user.email)
            except Exception as e:
                print(f"Error al enviar el correo: {e}")
        else:
            print("Error al generar el PDF")
    except Exception as e:
        print(f"Error al llamar a la función Lambda: {e}")
    
def send_email_with_pdf_link(pdf_link, recipient_email):
    # Configuración del servidor SMTP
    smtp_server = "smtp.outlook.com"  # Cambia según tu proveedor (e.g., smtp.outlook.com para Outlook)
    smtp_port = 587  # Puerto para TLS
    sender_email = "grupo6_arquisoftware@outlook.com"  # Cambia por tu correo
    sender_password = "Nomegustaarqui2024"  # Contraseña del correo o App Password si usas Gmail

    try:
        # Crear el mensaje de correo
        subject = "Tu PDF generado está listo"
        body = f"Hola,\n\nTu PDF está listo. Puedes descargarlo usando el siguiente enlace:\n\n{pdf_link}\n\nSaludos cordiales."
        
        # Configuración del correo
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Agregar el cuerpo al correo
        message.attach(MIMEText(body, "plain"))

        # Conectar al servidor SMTP y enviar el correo
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Iniciar cifrado TLS
            server.login(sender_email, sender_password)  # Autenticación
            server.sendmail(sender_email, recipient_email, message.as_string())  # Enviar correo

        print(f"Correo enviado exitosamente a {recipient_email}")

    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
    
# /users
class UserView(APIView):
    """
    Vista para manejar la creación de usuarios (POST) y listar todos los usuarios (GET).
    """

    # Lista de correos electrónicos de administradores
    ADMIN_EMAILS = ["alvaro.sotomayor@uc.cl", "admin@g6.com", "pascual.seplveda@uc.cl"]

    # GET: Obtener la lista de todos los usuarios
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # POST: Crear un nuevo usuario
    def post(self, request, *args, **kwargs):
        data = request.data

        # Verificar si el correo pertenece a un administrador
        if data.get('email') in self.ADMIN_EMAILS:
            data['is_admin'] = True  # Forzar is_admin=True para administradores

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminView(APIView):
    
    def get(self, request, user_id, *args, **kwargs):
        """
        Verifica si un usuario es administrador.
        Este endpoint espera que user_id se pase como parámetro en la URL.
        """
        try:
            # Busca al usuario por user_id
            user = User.objects.get(user_id=user_id)
            return Response({"is_admin": user.is_admin}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Si el usuario no existe, responde con is_admin=False
            return Response({"is_admin": False, "error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)


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
        if not user_id or not money_to_add:
            return Response({"error": "user y quantity son campos requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el usuario y su wallet
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Sumar el dinero a la wallet del usuario
            user.wallet += float(money_to_add)  # Convertir a float si la cantidad es decimal
            user.save()

            return Response({
                "message": "Cantidad agregada a la wallet exitosamente",
                "user_id": user_id,
                "new_balance": user.wallet
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Error al actualizar la wallet"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


# Compra de bonos reservados
class BuyBonos(APIView):

    # POST: Comprar bonos reservados
    def post(self, request, *args, **kwargs):
        request_data = request.data
        bono_id_request = request_data.get('request_id')  # Identifica el bono original
        user_id = request_data.get('user_id')  # Nuevo propietario del bono
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos que se quieren comprar
        cost_per_bonus = 1000  # Precio por cada bono
        method = request_data.get('wallet')  # Método de pago (True para wallet, False para webpay)

        try:
            # Buscar el bono original
            bono = Bonos.objects.get(request_id=bono_id_request)
        except Bonos.DoesNotExist:
            return Response({"error": f"Bono no encontrado: {bono_id_request}"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Buscar el fixture relacionado con el bono
            fixture = Fixture.objects.get(fixture_id=bono.fixture_id)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Buscar el nuevo usuario que adquirirá el bono
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar que el bono tiene suficientes unidades disponibles
        if bono.quantity < quantity:
            return Response({"error": "Cantidad de bonos insuficiente para la compra"}, status=status.HTTP_400_BAD_REQUEST)

        total_cost = cost_per_bonus * quantity

        # Validar método de pago y procesar la transacción
        if method:  # Pago con wallet
            if user.wallet < total_cost:
                return Response({"error": "Fondos insuficientes"}, status=status.HTTP_400_BAD_REQUEST)

            # Descontar el dinero de la billetera del usuario
            user.wallet -= total_cost
            user.save()

        else:  # Pago con Transbank
            try:
                session_id = user.user_id
                tx = Transaction(WebpayOptions(
                    IntegrationCommerceCodes.WEBPAY_PLUS,
                    "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
                    IntegrationType.TEST
                ))

                # Crear transacción en Webpay
                request_id = uuid6.uuid6()
                buy_order = str(request_id)[:20]
                resp = tx.create(
                    buy_order, session_id, total_cost, "https://web.arqui-2024-gspate.me/webpayresult"
                )
                token = resp.get("token")
                url = resp.get("url")
            except Exception as e:
                return Response({"error": f"Error en Transbank: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar la cantidad de bonos en el bono original
        bono.quantity -= quantity
        bono.save()

        # Crear un nuevo bono para el comprador
        try:
            new_bono = Bonos.objects.create(
                request_id=uuid6.uuid6(),
                fixture_id=bono.fixture_id,
                user_id=user.user_id,
                quantity=quantity,
                group_id=bono.group_id,
                league_name=bono.league_name,
                round=bono.round,
                date=bono.date,
                result=bono.result,
                seller=bono.seller,
                wallet=method,
                datetime=timezone.now()
            )
        except Exception as e:
            # Revertir la cantidad en caso de fallo
            bono.quantity += quantity
            bono.save()
            return Response({"error": f"Error al crear el nuevo bono: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Enviar información al job_master para calcular recomendaciones
        try:
            job_master_url = "http://producer:5000/job"
            data = {
                "user_id": user.user_id,
                "fixture_id": fixture.fixture_id,
            }
            response = requests.post(job_master_url, json=data)

            if response.status_code == 200:
                message = "Bonos transferidos exitosamente, dinero descontado y recomendaciones generadas"
            else:
                message = "Bonos transferidos exitosamente, dinero descontado, pero recomendaciones no generadas"
        except Exception as e:
            message = "Bonos transferidos exitosamente, pero no se generaron recomendaciones"

        # Responder con los detalles del nuevo bono
        return Response({
            "request_id": new_bono.request_id,
            "message": message,
            "quantity": new_bono.quantity,
            "total_cost": total_cost,
            "wallet": method,
            "token": token if not method else None,
            "url": url if not method else None
        }, status=status.HTTP_201_CREATED)
        

# Reserva de bonos
class ReserveBonos(APIView):

    # GET: Obtener los bonos reservados por el administrador
    def get(self, request, *args, **kwargs):
        # Obtener los usuarios administradores
        admin_users = User.objects.filter(is_admin=True)
        if not admin_users.exists():
            return Response({"error": "No se encontraron usuarios administradores"}, status=status.HTTP_404_NOT_FOUND)

        # Filtrar los bonos asociados a los administradores
        bonos = Bonos.objects.filter(user_id__in=admin_users.values_list('user_id', flat=True))
        serializer = BonosSerializer(bonos, many=True)

        return Response(serializer.data)

    # POST: Reservar bonos
    def post(self, request, *args, **kwargs):
        request_data = request.data
        fixture_id_request = request_data.get('fixture_id')
        user_id = request_data.get('user_id')  # Asumiendo que se pasa el user_id en la request
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos solicitados
        result = request_data.get('result')

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el usuario es administrador
        if not user.is_admin:
            return Response({"error": "Usuario no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generar un UUIDv6 para el request_id
        try:
            request_id = uuid6.uuid6()
        except:
            return Response({"error": "uuid6 failed"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la solicitud de bono
        bonus_request = Bonos.objects.create(
            request_id=request_id,
            fixture_id=fixture_id_request,
            user_id=user_id,
            quantity=quantity,
            group_id="6",
            league_name=fixture.league_name,
            round=fixture.league_round,
            datetime=timezone.now(),
            date=fixture.date,
            result=result,
            seller=6,
            wallet=False,
            acierto=False
        )

        token = 0  # deposit token

        data = {
            "request_id": str(bonus_request.request_id),
            "group_id": "6",
            "fixture_id": fixture_id_request,
            "league_name": fixture.league_name,
            "round": fixture.league_round,
            "date": fixture.date,
            "result": result,
            "deposit_token": f"{token}",
            "datetime": timezone.now(),
            "quantity": quantity,
            "wallet": bonus_request.wallet,
            "seller": 6
        }

        # Convertir el diccionario a una cadena JSON
        json_data = json.dumps(data, default=str)

        # Publicar el mensaje utilizando un cliente persistente
        try:
            client = mqtt.Client()
            client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
            client.connect(MQTT_HOST, MQTT_PORT, 60)

            # Publicar el mensaje en el tema correspondiente
            result = client.publish(MQTT_TOPIC, payload=json_data)
            result.wait_for_publish()  # Esperar confirmación de publicación
            client.disconnect()

            print(f"Mensaje publicado correctamente en '{MQTT_TOPIC}': {json_data}")
            return Response({"success": f"Bono reservado y publicado exitosamente: {json_data}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error al publicar en el broker MQTT: {e}")
            return Response({"error": f"Error al publicar en el broker: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# bonos
# Esta vista esta en desarrollo, no esta terminada
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
        result = request_data.get('result')


        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist: 
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        total_cost = cost_per_bonus * quantity

        if method: #Wallet
            # Validar si el usuario tiene suficiente dinero en su billetera
            if user.wallet < total_cost:
                return Response({"error": "Fondos insuficientes"}, status=status.HTTP_400_BAD_REQUEST)

            # Descontar el dinero de la billetera del usuario
            try:
                GenerateAndSendPdfToUserEmail(fixture, user)
            except:
                return Response({"error": "Problema al enviar el correo"}, status=status.HTTP_400_BAD_REQUEST)
            user.wallet -= total_cost
            user.save()

        else: #Transbank
            try:
                session_id = user.user_id
                try:
                    tx = Transaction(WebpayOptions(
                            IntegrationCommerceCodes.WEBPAY_PLUS, 
                            "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C", 
                            IntegrationType.TEST
                            ))

                            # Crea la transacción y obtiene el token y la URL
                    try:
                        request_id = uuid6.uuid6()
                        buy_order = str(request_id)[:20]
                    except:
                        return Response({"error": "uuid6 failed"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    resp = tx.create(buy_order, session_id, total_cost, "https://web.arqui-2024-gspate.me/webpayresult") 
                    token = resp.get("token")
                    url = resp.get("url")

                except Exception as e:
                    return Response({"error": f"Problema TBK tx {e}"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Validar si hay suficientes bonos disponibles
                if fixture.available_bonuses >= quantity:
                # Descontar temporalmente los bonos disponibles
                    fixture.available_bonuses -= quantity
                    fixture.save()

                if Bonos.objects.filter(request_id=request_id).exists():
                    return Response({"detail": "Request ID already exists."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    bonus_request = Bonos.objects.create(
                    request_id=request_id,
                    fixture_id=fixture.fixture_id,
                    user_id=user.user_id,
                    quantity=quantity,
                    group_id="6",
                    league_name=fixture.league_name,
                    round=fixture.league_round,
                    datetime=timezone.now(),# arreglar despues
                    date=fixture.date,
                    result=result,
                    seller=0,
                    wallet=method,
                    acierto=False
                    )
                except:
                    return Response({"error": "Problema TBK 1"}, status=status.HTTP_400_BAD_REQUEST)

                # PERO SI PUBLICAMOS AL MQTTT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\
                try:
                    data = {
                        "request_id": request_id,
                        "group_id": "6",
                        "fixture_id": fixture_id_request,
                        "league_name": fixture.league_name,
                        "round": fixture.league_round,
                        "date": fixture.date,
                        "result": result,
                        "deposit_token": token,
                        "datetime": timezone.now(),
                        "quantity": quantity,
                        "wallet": method,
                        "seller": 0
                    }
                except Exception as e:
                    return Response({"error": f"Problema TBK 2 {e}"}, status=status.HTTP_400_BAD_REQUEST)

                # Convertir el diccionario a una cadena JSON
                try:
                    json_data = json.dumps(data, default=str)

                    publish.single(
                        topic='fixtures/request',
                        payload=json_data,
                        hostname=MQTT_HOST,
                        port=MQTT_PORT,
                        auth={'username': MQTT_USER, 'password': MQTT_PASSWORD}
                    )
                except:
                    return Response({"error": "Problema TBK 3"}, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    job_master_url = "http://producer:5000/job"
                    data = {
                        "user_id": user.user_id,
                        "fixture_id": fixture.fixture_id,
                    }
                    response = requests.post(job_master_url, json=data)

                    if response.status_code == 200:
                        return Response({
                            "request_id": str(bonus_request.request_id),
                            "message": "Bonos comprados exitosamente, dinero descontado exitosamente y recomendaciones generadas", "token": token, "url": url
                        }, status=status.HTTP_201_CREATED)
                    else:

                        return Response({
                            "request_id": str(bonus_request.request_id),
                            "message": "Bonos comprados y dinero descontado exitosamente, pero recomendacion no generada", "token": token, "url": url
                        }, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    return Response({
                            "request_id": str(bonus_request.request_id),
                            "message": "Bonos comprados y dinero descontado exitosamente, pero recomendacion no generada", "token": token, "url": url
                        }, status=status.HTTP_201_CREATED)
                

            except Exception as e:
                # En caso de error, devuelve un mensaje
                return Response({"error": "Problemas en TBK", "detalle": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        
        # Validar si hay suficientes bonos disponibles
        if fixture.available_bonuses >= quantity:
            # Descontar temporalmente los bonos disponibles
            fixture.available_bonuses -= quantity
            fixture.save()

            # Generar un UUIDv6 para el request_id
            try:
                request_id = uuid6.uuid6()
            except:
                return Response({"error": "uuid6 failed"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la solicitud de bono
            bonus_request = Bonos.objects.create(
                request_id=request_id,
                fixture_id=fixture_id_request,
                user_id=user_id,
                quantity=quantity,
                group_id="6",
                league_name=fixture.league_name,
                round=fixture.league_round,
                datetime=timezone.now(),# arreglar despues
                date=fixture.date,
                result=request_data.get('result'),
                seller=0,
                wallet=request_data.get('wallet'),
                acierto=False
            )

            token = 0 # deposit token

            #PUBLICAMOS AL MQTTT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            data = {
                "request_id": str(bonus_request.request_id),
                "group_id": "6",
                "fixture_id": fixture_id_request,
                "league_name": fixture.league_name,
                "round": fixture.league_round,
                "date": fixture.date,
                "result": request_data.get('result'),
                "deposit_token": f"{token}",
                "datetime": timezone.now(),
                "quantity": quantity,
                "wallet": request_data.get('wallet'),
                "seller": 0
            }

            # Convertir el diccionario a una cadena JSON
            json_data = json.dumps(data, default=str)

            publish.single(
                topic='fixtures/request',
                payload=json_data,
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                auth={'username': MQTT_USER, 'password': MQTT_PASSWORD}
            )

            # Enviar información al job_master para calcular recomendaciones
            try:
                job_master_url = "http://producer:5000/job"
                data = {
                    "user_id": user.user_id,
                    "fixture_id": fixture.fixture_id,
                }
                response = requests.post(job_master_url, json=data)

                if response.status_code == 200:
                    try:
                        GenerateAndSendPdfToUserEmail(fixture, user)
                    except:
                        return Response({"error": "Problema al enviar el correo"}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({
                        "request_id": str(bonus_request.request_id),
                        "message": "Bonos comprados exitosamente, dinero descontado exitosamente y recomendaciones generadas"
                    }, status=status.HTTP_201_CREATED)
                else:
                    try:
                        GenerateAndSendPdfToUserEmail(fixture, user)
                    except:
                        return Response({"error": "Problema al enviar el correo"}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({
                        "request_id": str(bonus_request.request_id),
                        "message": "Bonos comprados y dinero descontado exitosamente, pero recomendacion no generada"
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                try:
                    GenerateAndSendPdfToUserEmail(fixture, user)
                except:
                    return Response({"error": "Problema al enviar el correo"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                        "request_id": str(bonus_request.request_id),
                        "message": "Bonos comprados y dinero descontado exitosamente, pero recomendacion no generada"
                    }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No hay suficientes bonos disponibles"}, status=status.HTTP_400_BAD_REQUEST)


class VerificarEstadoTransaccion(APIView):

    def post(self, request, *args, **kwargs):
        # Recibe el token_ws enviado por el frontend
        token_ws = request.data.get("token_ws")
    
        # Asegúrate de que request_id también se reciba en la solicitud
        # Verifica si el token_ws fue enviado
        if not token_ws:
            return Response({"error": "Token de transacción no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Confirma la transacción con Webpay usando el token_ws
            response = Transaction.commit(token_ws)

            request_id_cut = response['buy_order'] #ESTO QUEDA EN DUDA 
            try:
                bono_object = Bonos.objects.filter(request_id__startswith=request_id_cut).first()
            except:
                return Response({"error": "Token de transacción no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                data = {
                    "request_id": bono_object.request_id,
                    "group_id": "6",
                    "seller": 0,
                    "valid": True
                }

                # Convertir el diccionario a una cadena JSON
                json_data = json.dumps(data, default=str)
            except:
                return Response({"message": "Problema con data json dump"}, status=status.HTTP_404_NOT_FOUND)

            # Verifica el estado de la transacción
            if response['response_code'] == 0:
                try:
                    publish.single(
                        topic='fixtures/validations',
                        payload=json_data,
                        hostname=MQTT_HOST,
                        port=MQTT_PORT,
                        auth={'username': MQTT_USER, 'password': MQTT_PASSWORD}
                    )
                except:
                    return Response({"message": "problema con publish"}, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    "message": "Pago exitoso",
                    "buy_order": response['buy_order'],  # Acceso como clave de diccionario
                    "amount": response['amount'],        # Acceso como clave de diccionario
                    "transaction_date": response['transaction_date'],  # Acceso como clave de diccionario
                    "card_detail": response['card_detail'],  # Acceso como clave de diccionario
                    "status": response['status']  # Acceso como clave de diccionario
                }, status=status.HTTP_200_OK)

            else:
                # Si la transacción no es exitosa, devuelve el estado específico
                return Response({
                    "message": "La transacción no fue exitosa",
                    "status": response['status']  # Acceso como clave de diccionario
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Manejo de errores en caso de que falle la confirmación
            return Response({"error": "Error al confirmar la transacción", "detalle": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# heartbeat
class WorkersView(APIView):
    def get(self, request, *args, **kwargs):
        job_master_url = "http://producer:5000/heartbeat"
        try:
            response = requests.get(job_master_url, timeout=5)  # Añade un timeout
            response.raise_for_status()  # Lanza un error si el código HTTP no es 2xx

            # Intenta procesar el JSON
            try:
                data = response.json()
            except ValueError:
                return Response(
                    {"error": "La respuesta del servidor no es un JSON válido"},
                    status=500,
                )

            # Opcional: Estandarizar la respuesta
            return Response({"status": "success", "data": data}, status=200)

        except requests.exceptions.RequestException as e:
            # Manejar errores de conexión o tiempo de espera
            return Response(
                {"error": f"No se pudo conectar con el servidor: {str(e)}"},
                status=500,
            )


# mqtt/requests
class BonusRequestView(APIView):
    """
    Vista para almacenar solicitudes de compra de bonos desde el canal fixtures/requests.
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data
        fixture_id_request = request_data.get('fixture_id')
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos solicitados

        # Validar que el campo 'wallet' esté presente y sea booleano
        wallet = request_data.get('wallet')
        if wallet is None or not isinstance(wallet, bool):
            return Response({"error": "El campo 'wallet' es obligatorio y debe ser un valor booleano."}, status=status.HTTP_400_BAD_REQUEST)

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

        # Validar si el request_id ya existe
        request_id = request_data.get('request_id')
        validation = Bonos.objects.filter(request_id=request_id).exists()
        if validation:
            return Response({
                "error": f"Ya existe una solicitud con este request_id {request_id} {validation}."
            }, status=status.HTTP_409_CONFLICT)  # 409 Conflict

        # Validar si hay suficientes bonos disponibles
        if fixture.available_bonuses >= quantity:
            # Descontar temporalmente los bonos
            fixture.available_bonuses -= quantity
            fixture.save()

            # Intentar crear una nueva solicitud de bono (BonusRequest)
            try:
                bonus_request = Bonos.objects.create(
                    request_id=request_id,
                    fixture_id=fixture_id_request,
                    quantity=quantity,
                    group_id=request_data.get('group_id'),
                    league_name=request_data.get('league_name'),
                    round=request_data.get('round'),
                    date=formatted_date,  # Fecha corregida
                    result=request_data.get('result', '---'),
                    seller=request_data.get('seller', 0),
                    wallet=wallet,  # Ya se validó que sea un valor booleano
                    datetime=request_data.get('datetime')  # Usar el datetime que ya viene en el payload
                )
                return Response({
                    "request_id": bonus_request.request_id,
                    "message": "Bonos reservados temporalmente"
                }, status=status.HTTP_201_CREATED)
            
            except Exception:
                # Revertir el cambio en los bonos disponibles si hay un error
                fixture.available_bonuses += quantity
                fixture.save()
                return Response({
                    "error": f"Error al procesar la solicitud. Inténtalo nuevamente. {validation}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
            fixture = Fixture.objects.get(fixture_id=bonus_request.fixture_id)
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
                bonos = Bonos.objects.filter(fixture_id=fixture.fixture_id)

                for bono in bonos:
                    # Paso 5: Verificar si el bono ya fue procesado
                    if bono.status != 'pendiente':
                        continue

                    # Validar si el resultado del bono coincide con el del partido
                    if bono.result == match_result:
                        amount_to_credit = bono.quantity * 1000 * odds_value

                        try:
                            user = User.objects.get(user_id=bono.user_id)

                            if user:
                                user.wallet += amount_to_credit
                                user.save()
                                bono.status = 'ganado'
                                bono.save()
                            else:
                                bono.status = 'perdido'
                                bono.save()
                        except Exception as e:
                            continue

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

# mqtt/auctions
class AuctionsView(APIView):
    def post(self, request, *args, **kwargs):
        # Paso 1: Decodificar el JSON del request
        data = request.data

        # Validar que los campos obligatorios estén presentes
        required_fields = [
            "auction_id", "fixture_id", "league_name", "round", "result",
            "quantity", "group_id", "type"
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Faltan los campos obligatorios: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar fixture_id
        fixture_id_request = data.get("fixture_id")
        try:
            fixture_id_request = int(fixture_id_request)
        except ValueError:
            return Response(
                {"error": "El campo 'fixture_id' debe ser un número entero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist:
            return Response(
                {"error": "Fixture no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar y convertir tipos de datos
        try:
            quantity = int(data.get("quantity"))
            group_id = int(data.get("group_id"))
        except ValueError:
            return Response(
                {"error": "Los campos 'quantity' y 'group_id' deben ser números enteros"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Manejo por tipo de operación
        auction_type = data.get("type")

        if auction_type == "offer":
            # Validar que no exista una oferta con el mismo auction_id, proposal_id y type
            auction_id = data.get("auction_id")
            proposal_id = data.get("proposal_id", "")

            if Auctions.objects.filter(
                auction_id=auction_id, proposal_id=proposal_id, type=auction_type
            ).exists():
                return Response(
                    {
                        "error": "Auction con este auction_id, proposal_id y type ya existe.",
                        "auction_id": auction_id,
                        "proposal_id": proposal_id,
                        "type": auction_type,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            # Crear la subasta
            try:
                auction = Auctions.objects.create(
                    auction_id=auction_id,
                    proposal_id=proposal_id,
                    fixture_id=fixture_id_request,
                    league_name=data.get("league_name"),
                    round=data.get("round"),
                    result=data.get("result"),
                    quantity=quantity,
                    group_id=group_id,
                    type=auction_type,
                )
                return Response(
                    {
                        "auction_id": auction.auction_id,
                        "message": "Auction created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": f"Error al crear la subasta: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif auction_type == "proposal":
            # Validar condiciones para "proposal"
            auction_id = data.get("auction_id")
            existing_auction = Auctions.objects.filter(
                auction_id=auction_id, group_id=6, type="offer"
            ).first()

            if not existing_auction:
                return Response(
                    {"error": "No se encontró una oferta válida para esta propuesta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear la propuesta
            try:
                auction = Auctions.objects.create(
                    auction_id=auction_id,
                    proposal_id=data.get("proposal_id", ""),  # Valor por defecto vacío
                    fixture_id=fixture_id_request,
                    league_name=data.get("league_name"),
                    round=data.get("round"),
                    result=data.get("result"),
                    quantity=quantity,
                    group_id=group_id,
                    type=auction_type,
                )
                return Response(
                    {
                        "auction_id": auction.auction_id,
                        "message": "Proposal created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": f"Error al crear la propuesta: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        elif auction_type in ["acceptance", "rejection"]:
            # Manejo de aceptación o rechazo
            proposal_id = data.get("proposal_id")
            target_auction = Auctions.objects.filter(
                proposal_id=proposal_id, group_id=6, type="proposal"
            ).first()

            if not target_auction:
                return Response(
                    {"error": "No se encontró una propuesta válida para esta acción."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if auction_type == "rejection":
                # Rechazo: No se hace nada
                return Response(
                    {"message": "Propuesta rechazada. No se realizaron cambios."},
                    status=status.HTTP_200_OK,
                )

            elif auction_type == "acceptance": ###################### crear bono.
                # Aceptación: Actualizar el bono
                try:
                    bono = Bonos.objects.filter(
                        request_id=str(uuid6.uuid6()),
                        user_id= "google-oauth2|111781770565762915920",
                        fixture_id=data.get("fixture_id"),
                        league_name=data.get("league_name"),
                        round=data.get("round"),
                        result=data.get("result"),
                        group_id=6,
                        seller=6,  # Validar que sea de un admin
                        wallet=False,

                    ).first()

                    if not bono:
                        return Response(
                            {"error": "No se encontró un bono válido para la aceptación."},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    bono.quantity += quantity
                    bono.save()

                    return Response(
                        {"message": "Propuesta aceptada. Bono actualizado exitosamente."},
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    return Response(
                        {"error": f"Error al actualizar el bono: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        else:
            return Response(
                {"error": "Tipo de operación no válida."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AuctionsListView(APIView):
    """
    Vista para listar todas las subastas (Auctions).
    """
    def get(self, request, *args, **kwargs):
        # Obtener todos los registros de Auctions
        auctions = Auctions.objects.all()
        
        # Serializar los datos
        serializer = AuctionsSerializer(auctions, many=True)
        
        # Retornar la respuesta en formato JSON
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GroupProposalsView(APIView):
    """
    Vista para obtener todas las propuestas (proposals) asociadas al grupo con group_id=6.
    """
    def get(self, request, *args, **kwargs):
        try:
            # Buscar todas las auctions con group_id=6 y type="proposal"
            group_auctions = Auctions.objects.filter(type="proposal")

            # Extraer los auction_ids de las auctions del grupo
            group_auction_ids = group_auctions.values_list("auction_id", flat=True)

            # Buscar las auctions con proposal_id no vacío y cuyo auction_id pertenece al grupo
            proposals = Auctions.objects.filter(
                auction_id__in=group_auction_ids,
                proposal_id__isnull=False,
                type="proposal"
            ).exclude(proposal_id="")

            # Serializar las propuestas encontradas
            serializer = AuctionsSerializer(proposals, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Error al obtener las propuestas del grupo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
class OfferBonosView(APIView):
    def post(self, request, *args, **kwargs):
        # Paso 1: Validar el body de la request
        required_fields = ["fixture_id", "league_name", "round", "result", "quantity"]
        data = request.data
        user_id = data.get("user_id")

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el usuario es administrador
        if not user.is_admin:
            return Response({"error": "Usuario no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Faltan los campos obligatorios: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fixture_id = data.get("fixture_id")
        league_name = data.get("league_name")
        round_name = data.get("round")
        result = data.get("result")
        quantity = int(data.get("quantity", 0))

        # Paso 2: Buscar bonos válidos de administradores
        try:
            bono = Bonos.objects.filter(
                fixture_id=fixture_id,
                league_name=league_name,
                round=round_name,
                result=result,
                seller=6  # Solo bonos marcados como administradores
            ).first()

            if not bono:
                return Response(
                    {"error": "No se encontraron bonos válidos para la oferta."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Verificar que el bono pertenezca a un administrador
            user = User.objects.filter(user_id=bono.user_id, is_admin=True).first()
            if not user:
                return Response(
                    {"error": "El bono no pertenece a un administrador."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Verificar si la cantidad solicitada es válida
            if bono.quantity < quantity:
                return Response(
                    {"error": "La cantidad solicitada excede la cantidad disponible en el bono."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": f"Error al buscar bonos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Paso 3: Crear la oferta de subasta
        auction_id = uuid6.uuid6()

        payload = {
            "auction_id": str(auction_id),
            "proposal_id": "",
            "fixture_id": fixture_id,
            "league_name": league_name,
            "round": round_name,
            "result": result,
            "quantity": quantity,
            "group_id": 6,
            "type": "offer",
        }

        try:
            # Publicar el payload en el canal MQTT
            json_payload = json.dumps(payload)
            publish.single(
                topic=MQTT_AUC,
                payload=json_payload,
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                auth={"username": MQTT_USER, "password": MQTT_PASSWORD},
            )

            return Response(
                {"message": "Oferta publicada exitosamente.", "auction_id": str(auction_id)},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": f"Error al publicar en MQTT: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class SendProposalView(APIView):
    """
    Vista para enviar propuestas al canal MQTT fixtures/auctions.
    """

    def post(self, request, *args, **kwargs):
        # Datos esperados del frontend
        required_fields = ["auction_id", "fixture_id", "league_name", "round", "result", "quantity"]
        data = request.data
        user_id = data.get("user_id")

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el usuario es administrador
        if not user.is_admin:
            return Response({"error": "Usuario no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        # Validar campos obligatorios
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Faltan los campos obligatorios: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar y extraer datos del request
        try:
            auction_id = data["auction_id"]
            fixture_id = data["fixture_id"]
            league_name = data["league_name"]
            round = data["round"]
            result = data["result"]
            quantity = int(data["quantity"])
        except ValueError:
            return Response(
                {"error": "Los campos no estan en el formato correcto."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generar un nuevo proposal_id
        proposal_id = str(uuid6.uuid6())

        # Validar si existe un auction con el mismo auction_id
        try:
            auction = Auctions.objects.get(auction_id=auction_id)
        except Auctions.DoesNotExist:
            return Response(
                {"error": f"No se encontró un auction con auction_id {auction_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validar si la cantidad no excede la cantidad disponible en el auction original
        if quantity > auction.quantity:
            return Response(
                {"error": "La cantidad solicitada excede la cantidad disponible en el auction."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear el payload para enviar al canal MQTT
        payload = {
            "auction_id": auction_id,
            "proposal_id": proposal_id,
            "fixture_id": fixture_id,
            "league_name": league_name,
            "round": round,
            "result": result,
            "quantity": quantity,
            "group_id": 6, 
            "type": "proposal",
        }

        try:
            # Publicar el mensaje en el canal MQTT
            publish.single(
                topic=MQTT_AUC,
                payload=json.dumps(payload),
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                auth={"username": MQTT_USER, "password": MQTT_PASSWORD},
            )
            return Response(
                {"message": "Propuesta enviada exitosamente", "proposal_id": proposal_id},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error al enviar la propuesta al broker MQTT: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class ProposalResponseView(APIView):
    """
    Vista para aceptar o rechazar propuestas en el canal fixtures/auctions.
    """

    def post(self, request, *args, **kwargs):
        # Campos requeridos desde el frontend
        required_fields = [
            "auction_id", "proposal_id", "fixture_id", "league_name",
            "round", "result", "quantity", "type"
        ]
        data = request.data
        user_id = data.get("user_id")

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el usuario es administrador
        if not user.is_admin:
            return Response({"error": "Usuario no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        # Validar que los campos requeridos estén presentes
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Faltan los campos obligatorios: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar el tipo de acción
        action_type = data.get("type")
        if action_type not in ["acceptance", "rejection"]:
            return Response(
                {"error": "El campo 'type' debe ser 'acceptance' o 'rejection'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Si es un rechazo, no se realiza ninguna acción adicional
        if action_type == "rejection":
            # Publicar en MQTT que se rechazó la propuesta
            self.publish_to_mqtt(data, "rejection")
            return Response(
                {"message": "Propuesta rechazada exitosamente."},
                status=status.HTTP_200_OK,
            )

        # Si es una aceptación, buscar y actualizar los bonos
        try:
            # Buscar todos los bonos reservados que coincidan con los detalles y sean de admin
            bonos = Bonos.objects.filter(
                fixture_id=data["fixture_id"],
                league_name=data["league_name"],
                round=data["round"],
                result=data["result"],
                seller=6  # Solo bonos de admin
            )

            # Verificar si hay suficientes bonos disponibles en total
            total_quantity = bonos.aggregate(Sum('quantity'))['quantity__sum'] or 0
            if total_quantity < int(data["quantity"]):
                return Response(
                    {"error": "Cantidad insuficiente de bonos para aceptar la propuesta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Restar la cantidad solicitada de los bonos disponibles
            quantity_to_deduct = int(data["quantity"])
            for bono in bonos:
                if quantity_to_deduct == 0:
                    break  # Ya se cubrió la cantidad necesaria

                if bono.quantity >= quantity_to_deduct:
                    bono.quantity -= quantity_to_deduct
                    bono.save()
                    quantity_to_deduct = 0
                else:
                    quantity_to_deduct -= bono.quantity
                    bono.quantity = 0
                    bono.save()

            # Publicar en MQTT que se aceptó la propuesta
            self.publish_to_mqtt(data, "acceptance")

            return Response(
                {"message": "Propuesta aceptada exitosamente y bonos actualizados."},
                status=status.HTTP_200_OK,
            )

        except Bonos.DoesNotExist:
            return Response(
                {"error": "No se encontraron bonos que coincidan con la propuesta."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def publish_to_mqtt(self, data, action_type):
        """
        Publica la respuesta (aceptación o rechazo) en el canal MQTT.
        """
        payload = {
            "auction_id": data["auction_id"],
            "proposal_id": data["proposal_id"],
            "fixture_id": data["fixture_id"],
            "league_name": data["league_name"],
            "round": data["round"],
            "result": data["result"],
            "quantity": data["quantity"],
            "group_id": 6,  # Asume que el grupo es el 6
            "type": action_type
        }

        try:
            publish.single(
                topic=MQTT_AUC,
                payload=json.dumps(payload),
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                auth={"username": MQTT_USER, "password": MQTT_PASSWORD},
            )
        except Exception as e:
            raise Exception(f"Error al publicar en MQTT: {e}")
        

class DeleteAuctionView(APIView):
    """
    Vista para eliminar una auction específica basada en los campos proporcionados.
    """

    def delete(self, request, *args, **kwargs):
        # Campos requeridos desde el frontend
        required_fields = [
            "auction_id", "proposal_id", "fixture_id", "league_name",
            "round", "result", "quantity", "type"
        ]
        data = request.data
        user_id = data.get("user_id")

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar si el usuario es administrador
        if not user.is_admin:
            return Response({"error": "Usuario no autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        # Validar que los campos requeridos estén presentes
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Faltan los campos obligatorios: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar el tipo de auction
        if data.get("type") != "proposal":
            return Response(
                {"error": "El campo 'type' debe ser 'proposal'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Buscar y eliminar la auction que coincide con los detalles proporcionados
            auction = Auctions.objects.filter(
                auction_id=data["auction_id"],
                proposal_id=data["proposal_id"],
                fixture_id=data["fixture_id"],
                league_name=data["league_name"],
                round=data["round"],
                result=data["result"],
                quantity=data["quantity"],
                type=data["type"]
            )

            if not auction.exists():
                return Response(
                    {"error": "No se encontró ninguna auction que coincida con los criterios proporcionados."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            auction.delete()

            return Response(
                {"message": "Auction eliminada exitosamente."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error al eliminar la auction: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserPurchasesView(APIView):

    def get(self, request, user_id, *args, **kwargs):
        # Filtrar las compras por usuario
        bonos = Bonos.objects.filter(user_id=user_id)
        serializer = BonosSerializer(bonos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StoreRecommendationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RecommendationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRecommendationsView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        # Filtra las recomendaciones por el user_id especificado y ordena por benefit_score en orden descendente
        recommendations = Recommendation.objects.filter(user_id=user_id).order_by('-benefit_score')

        # Si no se encuentran recomendaciones, devuelve un mensaje informativo
        if not recommendations.exists():
            return Response({"message": "No hay recomendaciones para este usuario."}, status=status.HTTP_404_NOT_FOUND)

        # Obtiene los fixtures asociados con las recomendaciones en el orden de benefit_score
        fixture_ids = recommendations.values_list('fixture_id', flat=True)
        fixtures = Fixture.objects.filter(fixture_id__in=fixture_ids)

        # Serializa los fixtures encontrados
        serializer = FixtureSerializer(fixtures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# fix