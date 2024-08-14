from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .serializer import *
from .models import *


from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status,generics

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
    

# View all subcategories



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




    # ADMIN

# Add college

@api_view(['POST'])
def add_college(request):
    serializer = AddCollegeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# see subcategories

class AdminSubcategoryListView(generics.ListAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer


# Add category/subcategory

class CategorySubcategoryView(APIView):
    def post(self, request):
        data = request.data
        if data.get('type') == 'category':
            serializer = CategorySerializer(data=data)
        elif data.get('type') == 'subcategory':
            serializer = SubcategorySerializer(data=data)
        else:
            return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    


# Edit college

from rest_framework.parsers import MultiPartParser, FormParser

class AdminEditCollegeView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, pk):
        college = get_object_or_404(Colleges, pk=pk)
        serializer = EditCollegeSerializer(college, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Handle new other images
            new_other_images = request.FILES.getlist('new_other_images')
            for image in new_other_images:
                OtherImage.objects.create(college=college, image=image)
            return Response(serializer.data)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        college = get_object_or_404(Colleges, pk=pk)
        college.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DeleteOtherImageView(APIView):
    def delete(self, request, pk):
        other_image = get_object_or_404(OtherImage, pk=pk)
        other_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)










class CollegeDetailEditView(APIView):
    def get(self, request, pk):
        college = get_object_or_404(Colleges, pk=pk)
        serializer = CollegeSerializer(college)
        return Response(serializer.data)

    def put(self, request, pk):
        college = get_object_or_404(Colleges, pk=pk)
        serializer = CollegeSerializer(college, data=request.data, partial=True)
        if serializer.is_valid():
            # Handle main images
            image_fields = ['main_image', 'hostel_image', 'library_image', 'class_image', 'lab_image']
            for field in image_fields:
                if field in request.data:
                    if request.data[field] is None:
                        # Clear the image if None is sent
                        setattr(college, field, None)
                    elif isinstance(request.data[field], str):
                        if request.data[field].startswith('/images/'):
                            # It's an existing image URL, do nothing
                            pass
                        else:
                            # Invalid image data
                            return Response({'error': f'Invalid image data for {field}'}, status=status.HTTP_400_BAD_REQUEST)

            # Handle other fields
            for field in ['name', 'courses', 'location', 'priority']:
                if field in request.data:
                    setattr(college, field, request.data[field])

            # Handle other_images
            if 'other_images' in request.data:
                # Clear existing other images
                college.other_images.all().delete()
                # Add new other images if any
                for img_data in request.data['other_images']:
                    if isinstance(img_data['image'], str) and img_data['image'].startswith('/images/'):
                        # It's an existing image URL, create new OtherImage
                        OtherImage.objects.create(college=college, image=img_data['image'])

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        college = get_object_or_404(Colleges, pk=pk)
        college.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)










# SEARCH COLLEGE

from django.db import connection
from django.db.models import Q
from django.http import JsonResponse


def search_colleges(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'error': 'No search query provided.'}, status=400)

    # Check the database vendor
    if connection.vendor == 'postgresql':
        # PostgreSQL-specific full-text search
        from django.contrib.postgres.search import TrigramSimilarity
        colleges = Colleges.objects.annotate(
            similarity=TrigramSimilarity('name', query) + TrigramSimilarity('courses', query)
        ).filter(similarity__gt=0.3).order_by('-similarity')
    else:
        # Fallback for SQLite (or other databases)
        colleges = Colleges.objects.filter(
            Q(name__icontains=query) |
            Q(courses__icontains=query)
        )

    # Adjust how the results are formatted, especially for the main_image field
    results = [
        {
            'id': college.id,
            'name': college.name,
            'location': college.location,
            'main_image': college.main_image.url if college.main_image else None,
            'priority': college.priority,
        }
        for college in colleges
    ]

    return JsonResponse(results, safe=False)
