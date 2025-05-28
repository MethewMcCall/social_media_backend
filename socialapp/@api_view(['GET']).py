@api_view(['GET'])
def api_index(request):
    return Response({
        'message': 'Welcome to the Social Media API',
        'endpoints': {
            # endpoint details...
        }
    })