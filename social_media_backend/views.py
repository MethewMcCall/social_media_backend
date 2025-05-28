from django.http import HttpResponse

def welcome(request):
    return HttpResponse(
        "<h1>Welcome to Social Media API</h1>"
        "<p>API endpoints are available at <a href='/api/'>/api/</a></p>"
    )