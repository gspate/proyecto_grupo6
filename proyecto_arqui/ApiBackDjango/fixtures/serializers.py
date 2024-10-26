from rest_framework import serializers
from .models import Fixture, Bonos, User

class FixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixture
        fields = '__all__'


class BonosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonos
        fields = [
            'request_id', 'fixture', 'user', 'quantity', 'datetime', 'group_id', 'league_name', 'round', 
            'date', 'result', 'deposit_token', 'seller', 'wallet'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'wallet', 'created_at', 'updated_at']
