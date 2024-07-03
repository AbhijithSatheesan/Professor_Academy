from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    
)


urlpatterns = [

    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('index/', Index, name= 'index'),
    path('adduser/', UserRegisterView.as_view(), name='adduser'),
    path('profile/<int:pk>/', UserProfile.as_view() , name= 'userprofile'),
    path('markcollege/', add_marked_college, name='markcollege'),
    path('userslist', UsersList, name= 'userslist'),
    path('stats', UserAndCollegeStats, name='stats'),
    
]