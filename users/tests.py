from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import MyUsers, MarkedColleges
from colleges.models import Colleges

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = MyUsers.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.admin = MyUsers.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.college = Colleges.objects.create(name='Test College', location='Test Location')

    def test_user_login(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_add_marked_college(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('markcollege')
        data = {'user_id': self.user.id, 'college_id': self.college.id, 'fee': 5000}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(MarkedColleges.objects.filter(student=self.user, marked_college=self.college).exists())

    def test_user_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('userprofile', kwargs={'pk': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_admin_edit_user(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('admin-edit-user', kwargs={'user_id': self.user.id})
        data = {'username': 'updateduser'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_login_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)

    def test_add_marked_college_duplicate(self):
        MarkedColleges.objects.create(student=self.user, marked_college=self.college)
        self.client.force_authenticate(user=self.user)
        url = reverse('markcollege')
        data = {'user_id': self.user.id, 'college_id': self.college.id, 'fee': 5000}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Marked college removed')

    def test_non_admin_cant_edit_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('admin-edit-user', kwargs={'user_id': self.user.id})
        data = {'username': 'updateduser'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 403)




    def test_user_stats(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('student_count', response.data)
        self.assertIn('admin_count', response.data)
        self.assertIn('college_count', response.data)

    def test_password_reset_request(self):
        url = reverse('password-reset-request')
        data = {'email': self.user.email}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)




