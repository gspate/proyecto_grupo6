from rest_framework import generics
from .models import Fixture
from .serializers import FixtureSerializer
from django.utils.timezone import now
from django.db.models import Q

class FixtureList(generics.ListCreateAPIView):
    serializer_class = FixtureSerializer
    queryset = Fixture.objects.filter(date__gte=now())  # Only future matches
    pagination_class = None  # You can customize pagination here

    def get_queryset(self):
        queryset = super().get_queryset()
        home_team = self.request.query_params.get('home')
        away_team = self.request.query_params.get('away')
        date = self.request.query_params.get('date')

        if home_team:
            queryset = queryset.filter(home_team_name__icontains=home_team)
        if away_team:
            queryset = queryset.filter(away_team_name__icontains=away_team)
        if date:
            queryset = queryset.filter(date__date=date)

        return queryset

class FixtureDetail(generics.RetrieveUpdateAPIView):
    serializer_class = FixtureSerializer
    queryset = Fixture.objects.all()
    lookup_field = 'fixture_id'
