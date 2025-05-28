from django.test import TestCase
from django.contrib.auth.models import User
from socialapp.models import UserProfile, Post, Like, Connection


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio'
        )
    
    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertTrue(self.profile.slug)
    
    def test_profile_str_representation(self):
        self.assertEqual(str(self.profile), "testuser's Profile")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
    
    def test_post_creation(self):
        self.assertEqual(self.post.author.username, 'testuser')
        self.assertEqual(self.post.content, 'Test post content')
        self.assertEqual(self.post.likes_count, 0)
    
    def test_post_str_representation(self):
        self.assertTrue(str(self.post).startswith('Post by testuser'))


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Test post content'
        )
        self.like = Like.objects.create(
            user=self.user,
            post=self.post
        )
    
    def test_like_creation(self):
        self.assertEqual(self.like.user.username, 'testuser')
        self.assertEqual(self.like.post.content, 'Test post content')
        self.assertEqual(self.post.likes_count, 1)
    
    def test_like_str_representation(self):
        self.assertEqual(str(self.like), f"testuser likes {self.post.id}")


class ConnectionModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpassword1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword2'
        )
        self.connection = Connection.objects.create(
            sender=self.user1,
            receiver=self.user2
        )
    
    def test_connection_creation(self):
        self.assertEqual(self.connection.sender.username, 'testuser1')
        self.assertEqual(self.connection.receiver.username, 'testuser2')
        self.assertEqual(self.connection.status, 'pending')
    
    def test_connection_str_representation(self):
        self.assertEqual(str(self.connection), "testuser1 -> testuser2 (pending)")
    
    def test_are_connected_method(self):
        self.assertFalse(Connection.are_connected(self.user1, self.user2))
        self.connection.status = 'accepted'
        self.connection.save()
        self.assertTrue(Connection.are_connected(self.user1, self.user2))
    
    def test_get_user_connections_method(self):
        self.connection.status = 'accepted'
        self.connection.save()
        connections = Connection.get_user_connections(self.user1)
        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0], self.user2)