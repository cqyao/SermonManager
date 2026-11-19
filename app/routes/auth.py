import os
from flask import Blueprint, render_template, url_for, redirect

from flask_login import login_user, logout_user, login_required
import bcrypt
from ..user import User
from ..forms import LoginForm


auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        stored_hash = os.environ.get("PASSWORD").strip()
        
        try:
            # bcrypt.checkpw expects bytes for both password and hash
            result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            
            if result:
                user = User("1")
                login_user(user)
                return redirect(url_for("admin.admin"))
            else:
                return render_template("login.html", form=form, error="Invalid credentials")
        except Exception as e:
            print(f"Login error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return render_template("login.html", form=form, error="Authentication error")
    
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
