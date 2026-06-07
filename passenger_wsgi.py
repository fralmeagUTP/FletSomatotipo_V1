import os
import sys

from a2wsgi import ASGIMiddleware


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


from src.backend.main import app as asgi_app


# cPanel/Passenger expects a WSGI callable named "application".
application = ASGIMiddleware(asgi_app)
