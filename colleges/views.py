from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from .serializer import *
from .models import *


from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Create your views here.

# CATEGORY

@api_view(['GET'])
def CollegeCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many = True)
    
    return Response(serializer.data)


# SUBCATEGORY


@api_view(['GET'])
def category_subcategories(request, category_id):
    try:
        category = Category.objects.get(id= category_id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=404)


# sample data 
# http://localhost:8000/api/colleges/category/3/subcategories/


# COLLEGELIST

@api_view(['GET'])
def College_subcategories_list(request, subcategory_id):
    try:
        subcategory = Subcategory.objects.get(id=subcategory_id)
        colleges = Colleges.objects.filter(parent_subcategories=subcategory)
        serializer = CollegeListSerializer(colleges, many=True)
        return Response(serializer.data)
    except Subcategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=404)



# COLLEGE PAGE

@api_view(['GET'])
def college_detail(request, college_id):
    try:
        college = Colleges.objects.get(id=college_id)
        serializer = CollegeSerializer(college)
        return Response(serializer.data)
    except Colleges.DoesNotExist:
        return Response({'error': 'College not found'}, status=404)



















