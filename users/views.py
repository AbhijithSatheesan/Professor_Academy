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
from django.contrib.auth import get_user_model

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
        username = user.username
        
        # Retrieve the validated data (tokens)
        token = serializer.validated_data
        
        # Add custom user details
        token['authenticated'] = 'True'
        token['user_name'] = username
        token['marked_college_ids'] = marked_college_ids
        token['image'] = user.image.url if user.image else None
        token['user_id'] = user_id
        
         
        return Response(token, status=status.HTTP_200_OK)


# USERDETAILS

class UserProfile(APIView):
    def get(self, request, pk):
        User = get_user_model()
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        user_details = {
            'username': user.username,
            'email': user.email,
            'image': user.image.url if user.image else None,
            'user_type': user.user_type,
            'marked_colleges': []
        }

        marked_colleges = MarkedColleges.objects.filter(student=user)
        for marked_college in marked_colleges:
            college = marked_college.marked_college
            user_details['marked_colleges'].append({
                'college_id': college.id,
                'college_name': college.name,
                'category': college.category.name if college.category else None,
                'parent_subcategories': [subcategory.name for subcategory in college.parent_subcategories.all()],
                'courses': college.courses,
                'location': college.location,
                'priority': college.priority,
                'main_image': college.main_image.url if college.main_image else None, 
                'fee': marked_college.fee
            })

        return Response(user_details)














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
        # If the entry already exists, delete it (unlike)
        marked_college.delete()
        return Response({"message": "Marked college removed"}, status=status.HTTP_200_OK)
    
    # If the entry was created, return the new marked college
    serializer = MarkedCollegeSerializer(marked_college)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# {
#   "user_id": 1,
#   "college_id": 15,
#   "fee": 5000
# }