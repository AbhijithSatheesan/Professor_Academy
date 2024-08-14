from django.urls import path
from .views import *


urlpatterns = [

    path('categories', CollegeCategories, name='categories'),
    path('category/<int:category_id>/subcategories/', category_subcategories, name='category_subcategories'),
    path('subcategory/<int:subcategory_id>/colleges/', College_subcategories_list, name= 'subcategory_colleges'),

    path('searchcollege/', search_colleges, name='college-search'),

    # Admin
    path('seecollegedetails/<int:college_id>/', college_detail, name='college_details'),
    path('addcollege', add_college, name='add_college'),
    path('subcategories', AdminSubcategoryListView.as_view(), name='subcategorylist'),
    path('addcategories', CategorySubcategoryView.as_view(), name= 'addcategory'),
    path('updatecollege/<int:pk>/', AdminEditCollegeView.as_view(), name='update-college'),
    path('other-images/<int:pk>/', DeleteOtherImageView.as_view(), name='delete-other-image'),
]