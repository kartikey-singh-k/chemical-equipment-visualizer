from rest_framework import serializers
from .models import EquipmentBatch

class EquipmentBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentBatch
        fields = '__all__'