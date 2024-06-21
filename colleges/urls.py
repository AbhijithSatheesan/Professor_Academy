from django.urls import path
from .views import *


urlpatterns = [

    path('categories', CollegeCategories, name='categories'),
    path('category/<int:category_id>/subcategories/', category_subcategories, name='category_subcategories'),
    path('subcategory/<int:subcategory_id>/colleges/', College_subcategories_list, name= 'subcategory_colleges'),
    path('seecollegedetails/<int:college_id>/', college_detail, name='college_details'),
]