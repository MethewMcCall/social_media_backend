from django.urls import path
from knox import views as knox_views
from . import views

app_name = 'socialapp'

urlpatterns = [
    # API Index
    path('', views.api_index, name='api-index'),
    
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Posts
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<uuid:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<uuid:pk>/like/', views.like_post, name='like-post'),
    path('posts/<uuid:pk>/unlike/', views.unlike_post, name='unlike-post'),
    
    # Add these URL patterns to the urlpatterns list
    
    # Comments
    path('posts/<uuid:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<uuid:comment_id>/reply/', views.ReplyCreateView.as_view(), name='reply-create'),
    
    # Connections
    path('users/<int:pk>/connect/', views.connect_user, name='connect-user'),
    path('connections/incoming/', views.IncomingConnectionsView.as_view(), name='incoming-connections'),
    path('connections/<int:pk>/accept/', views.accept_connection, name='accept-connection'),
    path('connections/<int:pk>/decline/', views.decline_connection, name='decline-connection'),
    
    # Recommendations
    path('recommendations/', views.UserRecommendationsView.as_view(), name='user-recommendations'),
]