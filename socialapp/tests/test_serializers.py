from django.test import TestCase
from django.contrib.auth.models import User
from socialapp.models import UserProfile, Post, Like, Connection
from socialapp.serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    LoginSerializer, PostSerializer, ConnectionSerializer
)
from rest_framework.test import APIRequestFactory


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        self.serializer = UserSerializer(instance=self.user)
    
    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']))
    
    def test_username_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['username'], 'testuser')


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
        self.serializer = UserProfileSerializer(instance=self.profile)
    
    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['user', 'bio', 'profile_picture', 'slug', 'created_at', 'updated_at']))
    
    def test_bio_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['bio'], 'Test bio')


class RegisterSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.serializer = RegisterSerializer(data=self.user_data)
    
    def test_serializer_validation(self):
        self.assertTrue(self.serializer.is_valid())
    
    def test_password_mismatch_validation(self):
        data = self.user_data.copy()
        data['password_confirm'] = 'wrongpassword'
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class PostSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
        self.request = self.factory.get('/')
        self.request.user = self.user
        self.serializer = PostSerializer(instance=self.post, context={'request': self.request})
    
    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'author', 'content', 'image', 'likes_count', 'is_liked', 'created_at', 'updated_at']))
    
    def test_content_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['content'], 'Test post content')
    
    def test_is_liked_field(self):
        data = self.serializer.data
        self.assertFalse(data['is_liked'])
        
        # Create a like and test again
        Like.objects.create(user=self.user, post=self.post)
        serializer = PostSerializer(instance=self.post, context={'request': self.request})
        data = serializer.data
        self.assertTrue(data['is_liked'])