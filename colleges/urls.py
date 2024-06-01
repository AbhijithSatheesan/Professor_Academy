from django.urls import path
from .views import *


urlpatterns = [

    path('index', Index, name= 'index'),
    path('showcolleges', Showcolleges, name = 'showcolleges'),
    path('categories', CollegeCategories, name='categories'),
    path('category/<int:category_id>/subcategories/', category_subcategories, name='category_subcategories'),
    path('subcategory/<int:subcategory_id>/colleges/', College_subcategories, name= 'subcategory_colleges')
]