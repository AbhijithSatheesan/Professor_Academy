from rest_framework import serializers

from .models import *


# COLLGED ETAILS

class OtherImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherImage
        fields = ['id', 'image']



class CollegeSerializer(serializers.ModelSerializer):
    other_images = OtherImageSerializer(many=True, read_only=True)
    courses = serializers.CharField(allow_null=True, required=False)
    location = serializers.CharField(allow_null=True, required=False)

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
    colleges = CollegeSerializer(many=True, read_only=True, source='college_set')
    parent_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'priority', 'colleges', 'parent_category']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True, source='subcategory_set')

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'priority', 'subcategories']



    # ADMIN

# Add college

class AddCollegeSerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Subcategory.objects.all(),
        required=False
    )
    other_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Colleges
        fields = ['id', 'name', 'category', 'subcategories', 'courses', 'location', 'priority',
                  'main_image', 'hostel_image', 'library_image', 'class_image', 'lab_image', 'other_images']

    def create(self, validated_data):
        subcategories = validated_data.pop('subcategories', [])
        other_images = validated_data.pop('other_images', [])
        
        college = Colleges.objects.create(**validated_data)
        college.parent_subcategories.set(subcategories)

        for image in other_images:
            OtherImage.objects.create(college=college, image=image)

        return college
    

class AdminSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'




from django.core.files.base import ContentFile
import base64
import uuid


class EditCollegeSerializer(serializers.ModelSerializer):
    other_images = OtherImageSerializer(many=True, read_only=True)
    parent_subcategories = serializers.PrimaryKeyRelatedField(many=True, queryset=Subcategory.objects.all(), required=False)

    class Meta:
        model = Colleges
        fields = ['id', 'name', 'courses', 'location', 'priority', 'main_image', 
                  'hostel_image', 'library_image', 'class_image', 'lab_image', 
                  'parent_subcategories', 'other_images']

    def handle_image(self, image_data):
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # It's a base64 encoded image
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            return ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
        return image_data  # It's either a file or a URL

    def update(self, instance, validated_data):
        image_fields = ['main_image', 'hostel_image', 'library_image', 'class_image', 'lab_image']
        
        for attr, value in validated_data.items():
            if attr in image_fields:
                if value is not None:
                    setattr(instance, attr, self.handle_image(value))
            else:
                setattr(instance, attr, value)
        
        if 'parent_subcategories' in validated_data:
            instance.parent_subcategories.set(validated_data['parent_subcategories'])
        
        instance.save()
        return instance