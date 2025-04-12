from flask import Flask, render_template, redirect, url_for
from extensions import db, bcrypt, login_manager, migrate, csrf
from models import User
from config import Config
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.projects import projects_bp
    from routes.tasks import tasks_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(chatbot_bp)

    # Create instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Root route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
