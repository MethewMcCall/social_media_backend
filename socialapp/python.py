MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # This requires the django-cors-headers package
    'django.middleware.common.CommonMiddleware',
    # ...
]