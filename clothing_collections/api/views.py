from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .. import models
from . import serializers


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BatchSerializer
    queryset = models.Batch.objects.all()


# Create batch
# Upload RawItem for batch
# Process each RawItem per batch to create Item (final)