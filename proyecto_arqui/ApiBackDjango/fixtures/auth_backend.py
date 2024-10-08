import requests
from jose import jwt, JWTError
from rest_framework import authentication, exceptions

class Auth0JSONWebTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = self.verify_jwt(token)
        except JWTError:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (payload, None)

    def verify_jwt(self, token):
        # Fetch the public key from Auth0
        jwks_url = "https://<AUTH0_DOMAIN>/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience='<YOUR_API_IDENTIFIER>',  # Make sure this matches your Auth0 API identifier
                issuer=f"https://<AUTH0_DOMAIN>/"
            )
            return payload

        raise exceptions.AuthenticationFailed('Invalid token')
