from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions
from rest_framework.decorators import api_view

from .serializer import *
from .models import *

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.




# LOGIN

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        

        # Add custom claims
        token['name'] = user.username
        token['is_admin']= user.is_staff
        token['id'] = user.email

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = serializer.user
        
        marked_college_ids = list(MarkedColleges.objects.filter(student=user).values_list('marked_college_id', flat=True))
        user_id = user.id
        
        # Retrieve the validated data (tokens)
        token = serializer.validated_data
        
        # Add custom user details
        token['marked_college_ids'] = marked_college_ids
        token['image'] = user.image.url if user.image else None
        token['user_id'] = user_id
        
        return Response(token, status=status.HTTP_200_OK)


# USERDETAILS

@api_view(['GET'])
def GetUserProfile(request):
    user = request.user
    serializer = UserProfileSerializer(user, many = False)
    return Response(serializer.data)




def Index(request):
    data = {'message' : 'start'}
    return JsonResponse(data)

# USER REGISTRATION

class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)  # Add this line
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to make it working send user details like below

# {
#     "username": "testuse1r",
#     "email": "test1user@example.com",
#     "password": "1234"
# }




# MARKING COLLEGES

from colleges.models import Colleges

@api_view(['POST'])
def add_marked_college(request):
    user_id = request.data.get('user_id')
    college_id = request.data.get('college_id')
    fee = request.data.get('fee', None)
    
    if not user_id or not college_id:
        return Response({"error": "user_id and college_id are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        student = MyUsers.objects.get(id=user_id)
        college = Colleges.objects.get(id=college_id)
    except MyUsers.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Colleges.DoesNotExist:
        return Response({"error": "College not found"}, status=status.HTTP_404_NOT_FOUND)
    
    marked_college, created = MarkedColleges.objects.get_or_create(student=student, marked_college=college, defaults={'fee': fee})
    
    if not created:
        return Response({"error": "Marked college already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MarkedCollegeSerializer(marked_college)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# {
#   "user_id": 1,
#   "college_id": 15,
#   "fee": 5000
# }