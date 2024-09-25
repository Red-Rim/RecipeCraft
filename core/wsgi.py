"""
WSGI configuration for the RecipeCraft project.

This file exposes the WSGI callable as a module-level variable named `application`.

For additional details, refer to the Django documentation:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'core' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the WSGI application object
application = get_wsgi_application()
