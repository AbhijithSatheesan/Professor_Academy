from rest_framework import serializers

from .models import *


# COLLGED ETAILS

class OtherImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherImage
        fields = ['id', 'image']



class CollegeSerializer(serializers.ModelSerializer):
    other_images = OtherImageSerializer(many=True, read_only=True)

    class Meta:
        model = Colleges
        fields = ['id', 'name', 'courses', 'location', 'priority', 'main_image', 'hostel_image', 'library_image', 'class_image', 'lab_image', 'other_images']



# COLLEGE LIST

class CollegeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colleges
        fields = ['id', 'name', 'location', 'main_image', 'priority']
        


# SUBCATEGORY

class SubcategorySerializer(serializers.ModelSerializer):
    colleges = CollegeSerializer(many= True, read_only= True, source='college_set')
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'image', 'priority', 'colleges']


# CATEGORY
    
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True, source='subcategory_set')

    class Meta:
        model = Category
        fields = ['id','name', 'image', 'priority','subcategories']



