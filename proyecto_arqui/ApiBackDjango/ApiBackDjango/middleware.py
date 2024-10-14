import json
import requests
from django.conf import settings
from django.http import JsonResponse
from jose import jwt
from wallet.models import Wallet

def jwt_required(view_func):
    print('jwt_req called')

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

            # Obtener el JWKS de Auth0
            jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
            try:
                jwks = requests.get(jwks_url).json()
            except requests.exceptions.RequestException as e:
                return JsonResponse({'message': f'Error fetching JWKS: {str(e)}'}, status=500)

            # Buscar la clave RSA correspondiente al 'kid' del header
            for key in jwks['keys']:
                if key['kid'] == header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e'],
                    }
                    break

            if not rsa_key:
                raise ValueError('Unable to find the appropriate key.')

            # Decodificar y validar el JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=settings.API_IDENTIFIER,
                issuer=f"https://{settings.AUTH0_DOMAIN}/"
            )

            # Asignar la información del usuario al request
            request.user = payload

            # Verificar si el usuario ya tiene una wallet
            # Verificar si el usuario ya tiene una wallet
            user_id = payload['sub']  # El ID del usuario en Auth0

# Cambiar 'user_id' por 'auth0_user_id'
            wallet, created = Wallet.objects.get_or_create(auth0_user_id=user_id, defaults={'balance': 0.00})

            if created:
                print(f'Wallet creada para el usuario {user_id} con saldo inicial de 0.00')

            

        except jwt.ExpiredSignatureError:
            return JsonResponse({'message1': 'Token has expired'}, status=401)
        except jwt.JWTClaimsError:
            return JsonResponse({'message2': 'Invalid token claims'}, status=401)
        except Exception as e:
            print(f"Error processing token: {str(e)}")  # Imprimir el error en la consola
            return JsonResponse({'message3': str(e)}, status=401)
        except requests.exceptions.ConnectionError as e:
            e = "No response"

        return view_func(request, *args, **kwargs)

    return _wrapped_view