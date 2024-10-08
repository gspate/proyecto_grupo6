from rest_framework import serializers
from .models import Fixture, Bonos

class FixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixture
        fields = '__all__'

class BonosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonos
        fields = [
            'request_id', 'fixture', 'quantity', 'status', 
            'datetime', 'group_id', 'league_name', 'round', 
            'date', 'result', 'deposit_token', 'seller'
        ]
