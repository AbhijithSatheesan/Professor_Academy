from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from .serializer import *
from .models import *

# Create your views here.

def Index(request):
    return HttpResponse('Start')


@api_view(['GET'])
def Showcolleges(request):
    colleges = Colleges.objects.all()
    serializer = CollegeSerializer(colleges, many= True)

    return Response(serializer.data)



@api_view(['GET'])
def CollegeCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many = True)
    
    return Response(serializer.data)



@api_view(['GET'])
def category_subcategories(request, category_id):
    category = Category.objects.get(id=category_id)
    serializer = CategorySerializer(category)
    return Response(serializer.data)


# sample data 
# http://localhost:8000/api/colleges/category/3/subcategories/


@api_view(['GET'])
def College_subcategories(request, subcategory_id):
    try:
        subcategory = Subcategory.objects.get(id=subcategory_id)
        colleges = Colleges.objects.filter(parent_subcategory=subcategory)
        serializer = CollegeSerializer(colleges, many=True)
        return Response(serializer.data)
    except Subcategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=404)





# @api_view(['GET'])
# def College_subcategories(request, subcategory_id):
#     try:
#         subcategory = Subcategory.objects.get(id= subcategory_id)
#         colleges = Colleges.objects.filter(Parent_subcategory = subcategory)
#         serializer = SubcategorySerializer(colleges, many= True)
#         return Response(serializer.data)
    
#     except: Subcategory.DoesNotExist:
#         return Response({'error':'Subcategory not found'}, status=404)
