from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import Fixture, BonusRequest
from .serializers import FixtureSerializer, BonusRequestSerializer, BonusValidationSerializer
from django.utils.timezone import now
from datetime import datetime

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

# Vista para obtener detalles de un fixture específico
class FixtureDetail(APIView):


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
    
# Vista para manejar solicitudes de compra de bonos desde el canal fixtures/requests

class BonusRequestView(APIView):
    """
    Vista para crear una solicitud de bonos (BonusRequest).
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data
        fixture_id_request = request_data.get('fixture_id')
        quantity = int(request_data.get('quantity', 0))  # Cantidad de bonos solicitados

        try:
            fixture = Fixture.objects.get(fixture_id=fixture_id_request)
        except Fixture.DoesNotExist:
            return Response({"error": "Fixture no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Validar si hay suficientes bonos disponibles
        if fixture.available_bonuses >= quantity:
            # Descontar temporalmente los bonos
            fixture.available_bonuses -= quantity
            fixture.save()

            # Convertir la fecha a formato 'YYYY-MM-DD'
            raw_date = request_data.get('date')
            formatted_date = datetime.strptime(raw_date[:10], '%Y-%m-%d').date()

            # Crear una nueva solicitud de bono (BonusRequest)
            bonus_request = BonusRequest.objects.create(
                request_id=request_data.get('request_id'),
                fixture=fixture,
                quantity=quantity,
                group_id=request_data.get('group_id'),
                league_name=request_data.get('league_name'),
                round=request_data.get('round'),
                date=formatted_date,  # Fecha corregida
                result=request_data.get('result', '---'),
                seller=request_data.get('seller', 0)
            )

            return Response({
                "request_id": bonus_request.request_id,
                "message": "Bonos reservados temporalmente"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "No hay suficientes bonos disponibles"}, status=status.HTTP_400_BAD_REQUEST)

# Vista para procesar validaciones de solicitudes de bonos desde el canal fixtures/validation
class BonusValidationView(APIView):
    

    def put(self, request, request_id, *args, **kwargs):
        # Extraer la validación y el request_id
        validation_data = request.data

        # Verificar que tenemos el campo valid
        valid = validation_data.get('valid', None)
        if valid is None:
            return Response({"error": "El campo 'valid' no fue encontrado en los datos de validación"}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la solicitud de bonos
        try:
            bonus_request = BonusRequest.objects.get(request_id=request_id)
        except BonusRequest.DoesNotExist:
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
