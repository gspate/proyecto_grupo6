from rest_framework import serializers
from .models import Fixture, BonusRequest

class FixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixture
        fields = '__all__'

class BonusRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusRequest
        fields = [
            'request_id', 'fixture', 'quantity', 'status', 
            'datetime', 'group_id', 'league_name', 'round', 
            'date', 'result', 'deposit_token', 'seller'
        ]

class BonusValidationSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    valid = serializers.BooleanField()