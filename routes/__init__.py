import os
import importlib
from flask import Flask

def register_routes(app: Flask):
    """Dynamically load and register all routes from the routes folder"""
    routes_dir = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(routes_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"routes.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, f"{filename[:-3]}_bp"):
                app.register_blueprint(getattr(module, f"{filename[:-3]}_bp"))
