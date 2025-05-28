# Social_media_backend
  
A robust Django REST API backend for a social media platform with features including user authentication, posts, likes, comments, connections, and user recommendations.

## Features

- **User Authentication**
  - Token-based authentication using Django REST Knox
  - Register, login, logout functionality
  - Secure password handling

- **User Profiles**
  - Bio and profile picture
  - Unique slugs for profile URLs

- **Posts**
  - Create, read, update, delete posts
  - Image upload support
  - Likes and unlike functionality

- **Comments**
  - Comment on posts
  - Reply to comments (nested comments)

- **Connections**
  - Send connection requests
  - Accept/decline connection requests
  - View incoming connection requests

- **Recommendations**
  - User recommendations based on mutual connections

- **API Documentation**
  - Swagger/OpenAPI documentation
  - Interactive API testing interface

## Technology Stack

- **Backend**: Django 5.2+, Django REST Framework 3.14+
- **Authentication**: Django REST Knox
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Deployment**: Docker, Gunicorn, Nginx
- **Image Processing**: Pillow

## Project Structure

```
social_media_backend/
├── social_app/           # Main Django app
│   ├── models.py         # UserProfile, Post, Like, Connection models
│   ├── views.py          # All API views and endpoints
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # App URL configuration
│   └── admin.py          # Admin interface
├── social_media_backend/ # Django project settings
│   ├── settings.py       # Development settings
│   ├── settings_prod.py  # Production settings
│   └── urls.py           # Main URL configuration
├── requirements.txt      # Development dependencies
├── requirements.prod.txt # Production dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── manage.py             # Django management script
```

## Setup Instructions

### Development Environment

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd social_media_backend
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   # OR
   source env/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/
   - Swagger Documentation: http://127.0.0.1:8000/swagger/

### Production Environment

1. **Create .env file**

   Create a `.env` file in the project root with the following variables (based on `.env.example`):

   ```
   # Django settings
   DJANGO_SECRET_KEY=your-secure-secret-key
   DJANGO_SETTINGS_MODULE=social_media_backend.settings_prod

   # Database settings
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=db
   DB_PORT=5432
   ```

2. **Build and run with Docker Compose**

   ```bash
   docker-compose up -d --build
   ```

3. **Create a superuser in the Docker container**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   
## API Endpoints

### Authentication

- `POST /api/register/` - Register a new user
- `POST /api/login/` - Login and get authentication token
- `POST /api/logout/` - Logout (invalidate current token)
- `POST /api/logoutall/` - Logout from all devices (invalidate all tokens)

### Profile

- `GET /api/profile/` - Get current user's profile
- `PUT /api/profile/` - Update current user's profile

### Posts

- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create a new post
- `GET /api/posts/<uuid>/` - Get post details
- `PUT /api/posts/<uuid>/` - Update a post
- `DELETE /api/posts/<uuid>/` - Delete a post
- `POST /api/posts/<uuid>/like/` - Like a post
- `POST /api/posts/<uuid>/unlike/` - Unlike a post

### Comments

- `GET /api/posts/<uuid>/comments/` - List comments for a post
- `POST /api/posts/<uuid>/comments/` - Add a comment to a post
- `GET /api/comments/<id>/` - Get comment details
- `PUT /api/comments/<id>/` - Update a comment
- `DELETE /api/comments/<id>/` - Delete a comment
- `POST /api/comments/<id>/reply/` - Reply to a comment

### Connections

- `POST /api/users/<id>/connect/` - Send a connection request
- `GET /api/connections/incoming/` - List incoming connection requests
- `POST /api/connections/<id>/accept/` - Accept a connection request
- `POST /api/connections/<id>/decline/` - Decline a connection request

### Recommendations

- `GET /api/recommendations/` - Get user recommendations based on mutual connections

## Future Implementations

1. **Real-time Notifications**
   - Implement WebSockets for real-time notifications using Django Channels
   - Notify users about new likes, comments, and connection requests

2. **Advanced Search**
   - Add search functionality for users, posts, and hashtags
   - Implement filters for search results

3. **Media Optimization**
   - Add image compression and resizing
   - Support for video uploads and processing

4. **Analytics Dashboard**
   - Track user engagement metrics
   - Provide insights on post performance

5. **Enhanced Security**
   - Implement rate limiting
   - Add two-factor authentication

6. **Content Moderation**
   - Add reporting functionality for inappropriate content
   - Implement automated content filtering

7. **Mobile App Integration**
   - Optimize API for mobile clients
   - Add push notification support

## Testing

The project includes comprehensive test coverage for models, serializers, and views.


# Run all tests
python manage.py test

# Run specific test module
python manage.py test socialapp.tests.test_models
