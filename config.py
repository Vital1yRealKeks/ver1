
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Application configuration
    PROJECT_ROLES = ['admin', 'manager', 'member']
    TASK_STATUSES = ['To Do', 'In Progress', 'Done']

    # Chatbot configuration
    CHATBOT_ENABLED = True
    CHATBOT_NAME = "ProjectAssistant"