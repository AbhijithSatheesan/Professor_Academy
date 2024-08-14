from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializer import *
from .models import *

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404



# Create your views here.




# LOGIN

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        

        # Add custom claims
        token['name'] = user.username
        token['is_staff']= user.is_staff
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
        is_admin = user.is_staff
        
        # Retrieve the validated data (tokens)
        token = serializer.validated_data
        
        # Add custom user details
        token['authenticated'] = 'True'
        token['user_name'] = username
        token['marked_college_ids'] = marked_college_ids
        token['image'] = user.image.url if user.image else None
        token['user_id'] = user_id

        # To confuse if anyone try to #################################
        if is_admin:
            token['admission_placed'] = 113
        else:
            token['admission_placed'] = None
        
        
         
        return Response(token, status=status.HTTP_200_OK)


# USERDETAILS
@permission_classes([IsAuthenticated])
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



    # ADMIN PANEL
    
# user and college stats

from django.apps import apps

@api_view(['GET'])
def UserAndCollegeStats(request):
    user_stats = MyUsers.objects.values('user_type').annotate(count=Count('id'))
    
    student_count = 0
    admin_count = 0
    for stat in user_stats:
        if stat['user_type'] == UserType.STUDENT:
            student_count = stat['count']
        elif stat['user_type'] == UserType.ADMIN:
            admin_count = stat['count']

    college_count = 0
    try:
        college_count = apps.get_model('colleges', 'Colleges').objects.count()
    except LookupError:
        pass  # Handle the case where the model doesn't exist

    return Response({
        'student_count': student_count,
        'admin_count': admin_count,
        'college_count': college_count
    })


# userlist

@api_view(['GET'])
def UsersList(request):
    
    students = MyUsers.objects.filter(user_type = UserType.STUDENT).order_by('username')
    admin = MyUsers.objects.filter(user_type = UserType.ADMIN).order_by('username')

    student_serializer = AdminUsersListSerializer(students, many= True)
    admin_serializer = AdminUsersListSerializer(admin, many = True)

    return Response({
        'admins': admin_serializer.data,
        'students': student_serializer.data
        
    })



# Register User

class UserRegisterView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Only staff users can register new users."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Set superuser and staff status based on user_type
            user_type = serializer.validated_data.get('user_type')
            if user_type in ['admin', 'staff']:
                user.is_superuser = True
                user.is_staff = True
                user.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # For debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# to make it working send user details like below

# {
#     "username": "testuse1r",
#     "email": "test1user@example.com",
#     "password": "1234"
# }



# Register on  Admin
class AdminRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)  # For debugging
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Check if the user type is admin and add privileges
            if user.user_type == UserType.ADMIN:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                # Optional: Add the user to the admin group if you have one
                # admin_group, created = Group.objects.get_or_create(name='Admins')
                # admin_group.user_set.add(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # For debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



# Edit users


class AdminEditUserView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(MyUsers.objects.prefetch_related('marked_colleges'), id=user_id)
        serializer = AdminUserEditSerializer(user)
        return Response(serializer.data)

    def patch(self, request, user_id):
        user = get_object_or_404(MyUsers, id=user_id)
        serializer = AdminUserEditSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = get_object_or_404(MyUsers, id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AdminUpdateMarkedCollegeView(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(MyUsers, id=user_id)
        college_id = request.data.get('college_id')
        fee = request.data.get('fee')
        try:
            marked_college = MarkedColleges.objects.get(student=user, marked_college_id=college_id)
            marked_college.fee = fee
            marked_college.save()
            return Response({'status': 'fee updated'})
        except MarkedColleges.DoesNotExist:
            return Response({'status': 'marked college not found'}, status=status.HTTP_404_NOT_FOUND)

class AdminAddMarkedCollegeView(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(MyUsers, id=user_id)
        college_id = request.data.get('college_id')
        fee = request.data.get('fee')
        marked_college, created = MarkedColleges.objects.get_or_create(
            student=user,
            marked_college_id=college_id,
            defaults={'fee': fee}
        )
        if not created:
            marked_college.fee = fee
            marked_college.save()
        return Response({'status': 'marked college added/updated'})
    


class AdminUpdateMarked(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, user_id):
        try:
            # Get the user
            user = get_object_or_404(MyUsers, id=user_id)
            
            # Get the data from the request
            marked_id = request.data.get('marked_id')
            fee = request.data.get('fee')
            
            # Get the MarkedColleges instance
            marked_college = get_object_or_404(MarkedColleges, id=marked_id, student=user)
            
            # Update the fee
            serializer = AdminUpdateMarkedSerializer(marked_college, data={'fee': fee}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




# PASSWORD RESET VIEW


# views.py
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from .models import MyUsers

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(MyUsers, email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://localhost:5173/passwordresetconfirm/{uid}/{token}/"

        html_message = render_to_string('users/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })

        plain_message = strip_tags(html_message)

        subject = 'Password Reset Request'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        email = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        password = request.data.get('password')
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(MyUsers, pk=uid)

        if default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid token or token has expired.'}, status=status.HTTP_400_BAD_REQUEST)
