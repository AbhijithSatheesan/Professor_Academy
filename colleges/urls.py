from django.urls import path
from .views import *


urlpatterns = [

    path('index', Index, name= 'index'),
    path('showcolleges', Showcolleges, name = 'showcolleges'),
    path('categories', CollegeCategories, name='categories')
]