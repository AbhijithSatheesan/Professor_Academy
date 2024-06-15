from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


# AUTH

    # USER REGISTRATION

User = get_user_model() # Use this for more flexibility

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email','password')

    def create(self,validated_data):
        user = User.objects.create_user(**validated_data)
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