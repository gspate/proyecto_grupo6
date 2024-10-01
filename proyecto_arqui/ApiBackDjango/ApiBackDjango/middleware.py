import json
import requests
from django.conf import settings
from django.http import JsonResponse
from jose import jwt
from wallet.models import Wallet
from django.contrib import auth

def jwt_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        
        if not token:
            return JsonResponse({'message': 'Authorization header is expected'}, status=401)
        
        # Eliminar "Bearer " del token
        token = token.split(' ')[1]
        try:
            # Obtener la cabecera del token
            header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in requests.get(f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json').json()['keys']:
                if key['kid'] == header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e'],
                    }

            # Decodificar el token
            payload = jwt.decode(token, rsa_key, algorithms=['RS256'], audience=settings.API_IDENTIFIER)
            request.user = payload  # Guardar información del usuario en la solicitud

            # Verificar si el usuario ya tiene una wallet
            user_id = payload['sub']  # El ID del usuario en Auth0
            wallet, created = Wallet.objects.get_or_create(user_id=user_id, defaults={'balance': 0.00})
            
            if created:
                print(f'Wallet creada para el usuario {user_id} con saldo inicial de 0.00')

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=401)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
