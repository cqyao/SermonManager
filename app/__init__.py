import os

from dotenv import load_dotenv
from flask import Flask, current_app
from flask_login import LoginManager
from supabase import create_client
from datetime import datetime
from .user import User

#FLASK LOGIN SETUP
login_manager = LoginManager()
        
@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return User("1")
    return None

# Global functions


def create_app():
    load_dotenv()

    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.environ.get("SECRET_KEY")

    app.extensions["supabase"] = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )

    @app.context_processor
    def inject_series():
        """Make series available on all templates"""
        supabase = current_app.extensions["supabase"]
        series_response = supabase.table("series").select("*").order("name").execute()
        return dict(series=series_response.data or [])

    @app.template_filter("format_date")
    def format_date(value):
        return datetime.strptime(value, "%Y-%m-%d").strftime("%B %d, %Y")


    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    return app