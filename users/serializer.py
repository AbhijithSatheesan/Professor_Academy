from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


# AUTH

    # USER REGISTRATION

User = get_user_model() # Use this for more flexibility

class UserRegistrationSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'user_type', 'image')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        if image:
            user.image = image
            user.save()
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



# Edit user


class AdminMarkedCollegeSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='marked_college.name', read_only=True)

    class Meta:
        model = MarkedColleges
        fields = ['id', 'college_name', 'fee']

class AdminUserEditSerializer(serializers.ModelSerializer):
    marked_colleges = AdminMarkedCollegeSerializer(many=True, read_only=True)

    class Meta:
        model = MyUsers
        fields = ['id', 'username', 'email', 'user_type', 'image', 'marked_colleges']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['marked_colleges'] = AdminMarkedCollegeSerializer(instance.marked_colleges.all(), many=True).data
        return representation
    


    # i used a seperate serializer and view to update fee

class AdminUpdateMarkedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkedColleges
        fields = ['id', 'fee']

    def update(self, instance, validated_data):
        instance.fee = validated_data.get('fee', instance.fee)
        instance.save()
        return instance
