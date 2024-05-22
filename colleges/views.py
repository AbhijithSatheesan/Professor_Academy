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