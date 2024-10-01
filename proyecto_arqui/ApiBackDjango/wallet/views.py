from django.views import View
from django.http import JsonResponse
from wallet.models import Wallet
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from ApiBackDjango.middleware import jwt_required  # Asegúrate de que jwt_required esté disponible

# Class-Based View para obtener la información de la wallet
@method_decorator([jwt_required, require_http_methods(["GET"])], name='dispatch')
class WalletInfoView(View):
    
    def get(self, request, *args, **kwargs):
        user_id = request.user['sub']  # El ID del usuario en Auth0 (viene del token JWT)
        print("WalletInfoView GET called")

        try:
            wallet = Wallet.objects.get(user_id=user_id)
            wallet_data = {
                'user_id': wallet.user_id,
                'balance': wallet.balance
            }
            return JsonResponse(wallet_data, status=200)
        
        except Wallet.DoesNotExist:
            return JsonResponse({'error': 'Wallet not found'}, status=404)