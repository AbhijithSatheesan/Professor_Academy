from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Category, Subcategory, Colleges, OtherImage
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

User = get_user_model()

class CollegeAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        self.category = Category.objects.create(name='Test Category', priority=1)
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', parent_category=self.category, priority=1)
        self.college = Colleges.objects.create(name='Test College', category=self.category, priority=1)
        self.college.parent_subcategories.add(self.subcategory)

    def create_image(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_college_categories(self):
        url = reverse('categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Category')

    def test_category_subcategories(self):
        url = reverse('category_subcategories', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Category')
        self.assertEqual(len(response.data['subcategories']), 1)

    def test_college_subcategories_list(self):
        url = reverse('subcategory_colleges', args=[self.subcategory.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test College')

    def test_search_colleges(self):
        url = reverse('college-search') + '?query=Test'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], 'Test College')

    def test_college_detail(self):
        url = reverse('college_details', args=[self.college.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test College')

    def test_add_college(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('add_college')
        image = self.create_image()
        data = {
            'name': 'New College',
            'category': self.category.id,
            'parent_subcategories': [self.subcategory.id],
            'priority': 2,
            'main_image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Colleges.objects.count(), 2)

    def test_admin_subcategory_list(self):
        url = reverse('subcategorylist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Subcategory')

    def test_add_category(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('addcategory')
        image = self.create_image()
        data = {
            'type': 'category',
            'name': 'New Category',
            'priority': 2,
            'image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_update_college(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('update-college', args=[self.college.id])
        data = {
            'name': 'Updated College Name',
            'priority': 3
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.college.refresh_from_db()
        self.assertEqual(self.college.name, 'Updated College Name')
        self.assertEqual(self.college.priority, 3)

    def test_delete_other_image(self):
        self.client.force_authenticate(user=self.admin_user)
        other_image = OtherImage.objects.create(college=self.college, image='test_image.jpg')
        url = reverse('delete-other-image', args=[other_image.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(OtherImage.objects.count(), 0)

    def test_unauthenticated_access(self):
        url = reverse('add_college')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_access(self):
        non_admin = User.objects.create_user('user', 'user@example.com', 'userpass')
        self.client.force_authenticate(user=non_admin)
        url = reverse('add_college')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_category_id(self):
        url = reverse('category_subcategories', args=[999])  # Non-existent category ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_search_query(self):
        url = reverse('college-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_subcategory(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('addcategory')
        image = self.create_image()
        data = {
            'type': 'subcategory',
            'name': 'New Subcategory',
            'parent_category': self.category.id,
            'priority': 2,
            'image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subcategory.objects.count(), 2)

    def test_update_college_with_images(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('update-college', args=[self.college.id])
        main_image = self.create_image()
        other_image = self.create_image()
        data = {
            'name': 'Updated College with Image',
            'main_image': main_image,
            'new_other_images': [other_image]
        }
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.college.refresh_from_db()
        self.assertEqual(self.college.name, 'Updated College with Image')
        self.assertIsNotNone(self.college.main_image)
        self.assertEqual(self.college.other_images.count(), 1)

    def test_update_college_invalid_image(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('update-college', args=[self.college.id])
        invalid_image = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")
        data = {
            'name': 'Updated College with Invalid Image',
            'main_image': invalid_image
        }
        response = self.client.put(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        # Clean up any files created during tests
        for college in Colleges.objects.all():
            if college.main_image:
                college.main_image.delete()
            for other_image in college.other_images.all():
                other_image.image.delete()