import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'AFM-web-app-dev_v1.0'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from django.core.wsgi import get_wsgi_application

app = get_wsgi_application()

def handler(request):
    return app(request.environ, request.start_response)
