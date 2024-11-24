"""
URL configuration for ApiBackDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from fixtures.views import FixtureList, FixtureDetail, BonusRequestView, BonusValidationView, BonosView, BonusHistoryView, UserView, UserDetailView, addwallet, StoreRecommendationView, UserPurchasesView, UserRecommendationsView, VerificarEstadoTransaccion, WorkersView, ReserveBonos, BuyBonos, AdminView

# VerificarEstadoTransaccion

urlpatterns = [
    # Fixtures
    path('fixtures', FixtureList.as_view(), name='fixture_list'),
    path('fixtures/<str:fixture_id>', FixtureDetail.as_view(), name='fixture_detail'),

    # MQTT (No USUARIOS)
    path('mqtt/requests', BonusRequestView.as_view(), name='bonus_request'),
    path('mqtt/validations/<str:request_id>', BonusValidationView.as_view(), name='bonus_validation'),
    path('mqtt/history', BonusHistoryView.as_view(), name='bonus_history'),

    # Usuarios
    path('users', UserView.as_view(), name='user_list'),
    path('users/<str:user_id>', UserDetailView.as_view(), name='user_detail'),

    # Bonos
    path('bonos', BonosView.as_view(), name='bonos_list'),
    path('bonos/<str:requests_id>', BonosView.as_view(), name='bonos_list'), 
    path('wallet/add', addwallet.as_view(), name='add_funds'),
    path('bonos_reserved', BuyBonos.as_view(), name='buy_bonos'),

    # Recomendaciones
    path("store_recommendation", StoreRecommendationView.as_view(), name="store_recommendation"),
    path("user_purchases/<str:user_id>", UserPurchasesView.as_view(), name="user_purchases"),
    path("user_recommendations/<str:user_id>", UserRecommendationsView.as_view(), name="user_recommendations"),
    path("heartbeat", WorkersView.as_view(), name="heartbeat"),

    # TransbankConfirm
    path('confirmTBK',VerificarEstadoTransaccion.as_view(), name= "TBK_confirm"),

    # Admin
    path('reserve_bonos', ReserveBonos.as_view(), name='reserve_bonos'),
    path('admin', AdminView.as_view(), name='admin'),
]
