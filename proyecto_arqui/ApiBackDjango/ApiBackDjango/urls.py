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
from django.contrib import admin
from django.urls import path, re_path
from wallet.views import WalletInfoView
from fixtures.views import FixtureList, FixtureDetail  # Importa tus vistas de fixtures

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ruta ver dinero
    path('wallet/', WalletInfoView.as_view(), name='wallet_info'), #Valores wallet user, JWT
    re_path(r'^wallet$', WalletInfoView.as_view(), name='wallet_info_redirect'),  # Redirección
    # Rutas de fixtures
    path('api/fixtures/', FixtureList.as_view(), name='fixture-list'),  # Lista de fixtures
    path('api/fixtures/<int:fixture_id>/', FixtureDetail.as_view(), name='fixture-detail'),  # Detalle de un fixture
]