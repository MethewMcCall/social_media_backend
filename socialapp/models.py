from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
import uuid


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    slug = models.SlugField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username)
            slug = base_slug
            counter = 1
            while UserProfile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        db_table = 'user_profiles'


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=2000)
    image = models.ImageField(
        upload_to='post_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post by {self.author.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_connections')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_connections')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'connections'
        unique_together = ('sender', 'receiver')
        
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"
    
    @classmethod
    def are_connected(cls, user1, user2):
        """Check if two users are connected (accepted connection)"""
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2, status='accepted') |
            models.Q(sender=user2, receiver=user1, status='accepted')
        ).exists()
    
    @classmethod
    def get_user_connections(cls, user):
        """Get all accepted connections for a user"""
        connections = cls.objects.filter(
            models.Q(sender=user, status='accepted') |
            models.Q(receiver=user, status='accepted')
        )
        
        connected_users = []
        for conn in connections:
            if conn.sender == user:
                connected_users.append(conn.receiver)
            else:
                connected_users.append(conn.sender)
        
        return connected_users


# Add this to the end of the file, after the Connection model

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"