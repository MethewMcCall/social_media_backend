from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth.models import User
from django.db.models import Q, Count, Case, When, IntegerField
from django.shortcuts import get_object_or_404
# Add this to the imports at the top
from .models import UserProfile, Post, Like, Connection, Comment
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer,
    PostSerializer, LikeSerializer, ConnectionSerializer, UserRecommendationSerializer,
    CommentSerializer
)

# Add these view classes after the UserRecommendationsView
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).select_related('author')
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.select_related('author')
    
    def get_object(self):
        comment = get_object_or_404(Comment, id=self.kwargs['pk'])
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if comment.author != self.request.user:
                self.permission_denied(self.request, message="You can only edit your own comments")
        return comment


class ReplyCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        parent_comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        serializer.save(
            author=self.request.user,
            post=parent_comment.post,
            parent=parent_comment
        )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = AuthToken.objects.create(user)[1]
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token
        }, status=status.HTTP_201_CREATED)


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = AuthToken.objects.create(user)[1]
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('likes')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('likes')
    
    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if post.author != self.request.user:
                self.permission_denied(self.request, message="You can only edit your own posts")
        return post


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if created:
        return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Post already liked'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    try:
        like = Like.objects.get(user=request.user, post=post)
        like.delete()
        return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({'message': 'Post not liked yet'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_user(request, pk):
    target_user = get_object_or_404(User, id=pk)
    
    if target_user == request.user:
        return Response({'error': 'Cannot connect to yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if connection already exists
    existing_connection = Connection.objects.filter(
        Q(sender=request.user, receiver=target_user) |
        Q(sender=target_user, receiver=request.user)
    ).first()
    
    if existing_connection:
        return Response({'error': 'Connection already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    connection = Connection.objects.create(sender=request.user, receiver=target_user)
    serializer = ConnectionSerializer(connection)
    
    return Response({
        'message': 'Connection request sent successfully',
        'connection': serializer.data
    }, status=status.HTTP_201_CREATED)


class IncomingConnectionsView(generics.ListAPIView):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Connection.objects.filter(
            receiver=self.request.user,
            status='pending'
        ).select_related('sender', 'receiver')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_connection(request, pk):
    connection = get_object_or_404(
        Connection,
        id=pk,
        receiver=request.user,
        status='pending'
    )
    
    connection.status = 'accepted'
    connection.save()
    
    serializer = ConnectionSerializer(connection)
    return Response({
        'message': 'Connection accepted successfully',
        'connection': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decline_connection(request, pk):
    connection = get_object_or_404(
        Connection,
        id=pk,
        receiver=request.user,
        status='pending'
    )
    
    connection.status = 'declined'
    connection.save()
    
    serializer = ConnectionSerializer(connection)
    return Response({
        'message': 'Connection declined successfully',
        'connection': serializer.data
    })


class UserRecommendationsView(generics.ListAPIView):
    serializer_class = UserRecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        current_user = self.request.user
        
        # Get users that are already connected
        connected_user_ids = set()
        connections = Connection.objects.filter(
            Q(sender=current_user, status='accepted') |
            Q(receiver=current_user, status='accepted')
        )
        
        for conn in connections:
            if conn.sender == current_user:
                connected_user_ids.add(conn.receiver.id)
            else:
                connected_user_ids.add(conn.sender.id)
        
        # Get users with pending connections
        pending_user_ids = set()
        pending_connections = Connection.objects.filter(
            Q(sender=current_user, status='pending') |
            Q(receiver=current_user, status='pending')
        )
        
        for conn in pending_connections:
            if conn.sender == current_user:
                pending_user_ids.add(conn.receiver.id)
            else:
                pending_user_ids.add(conn.sender.id)
        
        # Exclude current user, connected users, and users with pending connections
        excluded_user_ids = connected_user_ids | pending_user_ids | {current_user.id}
        
        # Get mutual connections count for recommendation scoring
        users = User.objects.exclude(id__in=excluded_user_ids).annotate(
            mutual_connections_count=Count(
                Case(
                    When(
                        Q(sent_connections__receiver__in=connected_user_ids, sent_connections__status='accepted') |
                        Q(received_connections__sender__in=connected_user_ids, received_connections__status='accepted'),
                        then=1
                    ),
                    output_field=IntegerField()
                )
            )
        ).select_related('profile').order_by('-mutual_connections_count', '?')[:10]
        
        return users


# Add this at the end of the file

@api_view(['GET'])
@permission_classes([AllowAny])
def api_index(request):
    return Response({
        'message': 'Welcome to the Social Media API',
        'endpoints': {
            'authentication': {
                'register': '/api/register/',
                'login': '/api/login/',
                'logout': '/api/logout/',
            },
            'profile': '/api/profile/',
            'posts': {
                'list_create': '/api/posts/',
                'detail': '/api/posts/{post_id}/',
                'like': '/api/posts/{post_id}/like/',
                'unlike': '/api/posts/{post_id}/unlike/',
                'comments': '/api/posts/{post_id}/comments/',
            },
            'comments': {
                'detail': '/api/comments/{comment_id}/',
                'reply': '/api/comments/{comment_id}/reply/',
            },
            'connections': {
                'connect': '/api/users/{user_id}/connect/',
                'incoming': '/api/connections/incoming/',
                'accept': '/api/connections/{connection_id}/accept/',
                'decline': '/api/connections/{connection_id}/decline/',
            },
            'recommendations': '/api/recommendations/',
        }
    })