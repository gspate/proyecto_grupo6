from rest_framework import serializers
from .models import Fixture, Bonos, User, Recommendation, Auctions

class FixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixture
        fields = '__all__'


class BonosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonos
        fields = [
            'request_id', 'fixture_id', 'user_id', 'quantity', 'datetime', 'group_id', 'league_name', 'round',
            'date', 'result', 'deposit_token', 'seller', 'wallet', 'acierto', 'status'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'wallet', 'is_admin']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class AuctionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auctions
        fields = '__all__'  
