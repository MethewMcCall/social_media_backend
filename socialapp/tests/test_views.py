from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from socialapp.models import UserProfile, Post, Like, Connection
import uuid


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('socialapp:register')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
    
    def test_register_with_mismatched_passwords(self):
        self.user_data['password_confirm'] = 'wrongpassword'
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('socialapp:login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_login_user(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_with_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('socialapp:profile')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.profile = UserProfile.objects.create(user=self.user, bio='Test bio')
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Test bio')
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_profile(self):
        data = {'bio': 'Updated bio'}
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Updated bio')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')


class PostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.posts_url = reverse('socialapp:post-list-create')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
        self.post_detail_url = reverse('socialapp:post-detail', kwargs={'pk': self.post.id})
    
    def test_create_post(self):
        data = {'content': 'New post content'}
        response = self.client.post(self.posts_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'New post content')
        self.assertEqual(Post.objects.count(), 2)
    
    def test_get_posts(self):
        response = self.client.get(self.posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_post_detail(self):
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test post content')
    
    def test_update_post(self):
        data = {'content': 'Updated content'}
        response = self.client.patch(self.post_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated content')
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'Updated content')
    
    def test_delete_post(self):
        response = self.client.delete(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)