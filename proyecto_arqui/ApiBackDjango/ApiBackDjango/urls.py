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
from fixtures.views import FixtureList, FixtureDetail, BonusRequestView, BonusValidationView, BonosView

urlpatterns = [
    # Fixtures
    path('fixtures', FixtureList.as_view(), name='fixture_list'),
    path('fixtures/<str:fixture_id>', FixtureDetail.as_view(), name='fixture_detail'),

    # MQTT (No USUARIOS)
    path('mqtt/requests', BonusRequestView.as_view(), name='bonus_request'),
    path('mqtt/validations/<str:request_id>', BonusValidationView.as_view(), name='bonus_validation'),

    # Usuarios
    # path('users', UserView.as_view(), name='user_list'),
    # path('users/<int:id>', UserDetailView.as_view(), name='user_list'),

    # Bonos
    path('bonos', BonosView.as_view(), name='bonos_list')
    # path('bonos/<str:requests_id>', BonosView.as_view(), name='bonos_list'),
]
