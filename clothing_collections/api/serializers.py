from rest_framework import serializers

from .. import models


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Batch
        fields = (
            'id',
            'name',
            'slug',
        )
        read_only_fields = ('slug',)


