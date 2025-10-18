from django.http import HttpResponse
from rest_framework import viewsets

from .models import Report
from .serializers import ReportSerializer 

def index(request):
    return HttpResponse("Hello there")

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer