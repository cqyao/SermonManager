#IMPORTS
from select import select
import uuid

from dotenv import load_dotenv


from flask import Flask, render_template, request, redirect, url_for
import os
from supabase import create_client
from datetime import datetime

# Password protection for selected routes
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

# Github webhook automation
import git

#LOAD ENVIRONMENT VARIABLES FROM .ENV FILE
load_dotenv()  

#CREATE FLASK APP
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

#SUPABASE CLIENT
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#FLASK LOGIN SETUP
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#FLASK USER SETUP
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        
@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return User("1")
    return None


#ROUTES
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        stored_hash = os.environ.get("PASSWORD").strip()
        
        try:
            # bcrypt.checkpw expects bytes for both password and hash
            result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            
            if result:
                user = User("1")
                login_user(user)
                return redirect(url_for("admin"))
            else:
                return render_template("login.html", error="Invalid credentials")
        except Exception as e:
            print(f"Login error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return render_template("login.html", error="Authentication error")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.context_processor
def inject_series():
    """Make series available on all templates"""
    series_response = supabase.table("series").select("*").order("name").execute()
    return dict(series=series_response.data or [])

@app.template_filter("format_date")
def fomrat_dat(value):
    return datetime.strptime(value, "%Y-%m-%d").strftime("%B %d, %Y")

# Home page
@app.route("/")
def index():
    sermons_response = supabase.table("sermons") \
        .select("*, series:series_id(name)") \
        .order("date", desc=True) \
        .execute()
    sermons = sermons_response.data

    return render_template("index.html", sermons=sermons)

# All sermons
@app.route("/sermons")
def sermons():
    date_filter = request.args.get("date")
    speaker_filter = request.args.get("speaker")
    book_filter = request.args.get("book")
    series_filter = request.args.get("series")
    
    query = supabase.table("sermons") \
        .select("*, series:series_id(name, image_url)")
    
    # Apply speaker filter
    if speaker_filter:
        query = query.eq("speaker", speaker_filter)
        
    # Apply book filter
    if book_filter:
        query = query.eq("book", book_filter)
        
    # Apply series filter
    if series_filter:
        # First find the series ID based on the name
        series_response = supabase.table("series").select("id").eq("name", series_filter).single().execute()
        if series_response.data:
            series_id = series_response.data["id"]
            query = query.eq("series_id", series_id)
    
    
    # Apply date sort
    response = query.order("date", desc=date_filter != "DATE_ASC").execute()
    
    sermons = response.data
    
    # Always render the full series, books, and speakers list in dropdowns
    series_response = supabase.table("series").select("name").order("name").execute()
    all_series = series_response.data or []
    
    speaker_response = supabase.table("unique_speakers").select("*").execute()
    book_response = supabase.table("unique_books").select("*").execute()

    return render_template("sermons.html", sermons=sermons, all_series=all_series, all_books=book_response, all_speakers=speaker_response)
    

# Individual series page
@app.route("/series/<int:series_id>")
def series(series_id):
    series_response = supabase.table("series") \
        .select("*") \
        .eq("id", series_id) \
        .single() \
        .execute()
    current_series = series_response.data

    sermons_response = supabase.table("sermons") \
        .select("*") \
        .eq("series_id", series_id) \
        .order("date", desc=True) \
        .execute()
    sermons = sermons_response.data

    return render_template("series.html", current_series=current_series, sermons=sermons)

# Individual sermon page
@app.route("/sermon/<int:sermon_id>")
def sermon(sermon_id):
    response = supabase.table("sermons") \
        .select("*, series:series_id(name)") \
        .eq("id", sermon_id) \
        .single() \
        .execute()
    sermon = response.data
    return render_template("sermon.html", sermon=sermon)

# Admin page
@app.route("/admin")
@login_required
def admin():
    sermons_response = supabase.table("sermons") \
        .select("*, series:series_id(name)") \
        .order("date", desc=True) \
        .execute()
    sermons = sermons_response.data

    series_response = supabase.table("series") \
        .select("*") \
        .execute()
    series = series_response.data
    
    images = []
    image_metadata = supabase.storage.from_("images").list()
    for filename in image_metadata: 
        image_url = supabase.storage.from_("images").get_public_url(filename['name'])
        images.append(image_url)


    return render_template("admin.html", sermons=sermons, series=series, images=images)

# Add series
@app.route("/admin/add-series", methods=["POST"])
def add_series():
    image_url = None
    
    # First, check if user selected an existing image
    selected_image_url = request.form.get("selected_image_url", "").strip()
    if selected_image_url:
        image_url = selected_image_url
    # Otherwise, handle uploading a new image if provided
    elif "image" in request.files:
        file = request.files["image"]
        if file.filename != "":
            extension = file.filename.rsplit(".", 1)[-1]
            filename = f"{uuid.uuid4()}.{extension}"
            
            supabase.storage.from_("images").upload(
                path=filename,
                file=file.read(),
                file_options={"content-type": file.content_type}
            )
            image_url = supabase.storage.from_("images").get_public_url(filename)
            
    supabase.table("series").insert({
        "name": request.form["name"],
        "series_description": request.form["description"],
        "image_url": image_url
    }).execute()
    
    return redirect(url_for("admin"))

# Add sermon
@app.route("/admin/add-sermon", methods=["POST"])
def add_sermon():
    image_url = None
        # First, check if user selected an existing image
    selected_image_url = request.form.get("selected_image_url", "").strip()
    if selected_image_url:
        image_url = selected_image_url
    # Otherwise, handle uploading a new image if provided
    elif "image" in request.files:
        file = request.files["image"]
        if file.filename != "":
            extension = file.filename.rsplit(".", 1)[-1]
            filename = f"{uuid.uuid4()}.{extension}"
            
            supabase.storage.from_("images").upload(
                path=filename,
                file=file.read(),
                file_options={"content-type": file.content_type}
            )
            image_url = supabase.storage.from_("images").get_public_url(filename)
    series_id = request.form["series_id"]
    supabase.table("sermons").insert({
        "title": request.form["title"],
        "date": request.form["date"],
        "speaker": request.form["speaker"],
        "topic": request.form["topic"],
        "book": request.form["book"],
        "audio_url": request.form["audio_url"],
        "image_url": image_url,
        "series_id": int(series_id) if series_id else None
    }).execute()
    return redirect(url_for("admin"))

# Delete sermon
@app.route("/admin/delete-sermon/<int:sermon_id>", methods=["POST"])
def delete_sermon(sermon_id):
    supabase.table("sermons").delete().eq("id", sermon_id).execute()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
    
# FOR GITHUB CI/CD AUTOMATION
@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('./SermonManager')
        origin = repo.remotes.origin
        
        origin.pull()
        return 'updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400
    


