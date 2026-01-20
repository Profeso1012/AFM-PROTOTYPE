import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AFM-web-app-dev_v1.0'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

application = get_wsgi_application()
