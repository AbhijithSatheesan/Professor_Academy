from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


# AUTH

    # USER REGISTRATION

User = get_user_model() # Use this for more flexibility

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'user_type','image')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            image=validated_data['image'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        return user


# USER INFO

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUsers
        fields = ['username', 'image']



# MARKED COLLEGES
class MarkedCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkedColleges
        fields = ['student','marked_college','fee']




# ADMIN

# User list

class AdminUsersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUsers
        fields = ['id', 'username', 'image', 'user_type']