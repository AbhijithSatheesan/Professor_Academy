from rest_framework import serializers

from .models import *


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colleges
        fields = '__all__'

    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'