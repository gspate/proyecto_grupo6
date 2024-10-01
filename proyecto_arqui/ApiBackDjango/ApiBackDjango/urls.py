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
from fixtures.views import FixtureList, FixtureDetail, BonusRequestView, BonusValidationView

urlpatterns = [
    path('fixtures', FixtureList.as_view(), name='fixture-list'),
    path('fixtures/<int:fixture_id>', FixtureDetail.as_view(), name='fixture-detail'),
    path('bonus/request', BonusRequestView.as_view(), name='bonus-request'),
    path('bonus/request/<str:request_id>/', BonusValidationView.as_view(), name='bonus-validate'),
]
