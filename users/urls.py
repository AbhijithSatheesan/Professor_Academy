from django.urls import path,include
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
    

    
    path('stats', UserAndCollegeStats, name='stats'),
    
    # admin
    path('userslist', UsersList, name= 'userslist'),
    path('admin-users/<int:user_id>/', AdminEditUserView.as_view(), name='admin-edit-user'),
    path('admin-users/<int:user_id>/update-marked-college/', AdminUpdateMarked.as_view(), name='admin-update-marked-college'),
    # path('admin-users/<int:user_id>/add-marked-college/', AdminAddMarkedCollegeView.as_view(), name='admin-add-marked-college'),


    # password reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
     
    
]