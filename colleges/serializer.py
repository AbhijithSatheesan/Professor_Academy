from rest_framework import serializers

from .models import *


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colleges
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    colleges = CollegeSerializer(many= True, read_only= True, source='college_set')
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'image', 'priority', 'colleges']

    
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True, source='subcategory_set')

    class Meta:
        model = Category
        fields = ['id','name', 'image', 'priority','subcategories']


