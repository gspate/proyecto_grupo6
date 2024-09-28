from rest_framework import serializers
from .models import Fixture

class FixtureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixture
        fields = '__all__'