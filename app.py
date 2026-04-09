from select import select

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from flask import Flask, render_template, request, redirect, url_for
import os
from supabase import create_client

# Store these in a .env file, never hardcode them
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Home page
@app.route("/")
def index():
    return render_template("index.html")

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
    
    # Always render the full series list in the series dropdown
    series_response = supabase.table("series").select("name").order("name").execute()
    all_series = series_response.data or []

    return render_template("sermons.html", sermons=sermons, all_series=all_series)

# Individual series page
@app.route("/series/<int:series_id>")
def series(series_id):
    series_response = supabase.table("series") \
        .select("*") \
        .eq("id", series_id) \
        .single() \
        .execute()
    series = series_response.data

    sermons_response = supabase.table("sermons") \
        .select("*") \
        .eq("series_id", series_id) \
        .order("date", desc=True) \
        .execute()
    sermons = sermons_response.data

    return render_template("series.html", series=series, sermons=sermons)

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

    return render_template("admin.html", sermons=sermons, series=series)

# Add series
@app.route("/admin/add-series", methods=["POST"])
def add_series():
    supabase.table("series").insert({
        "name": request.form["name"],
        "image_url": request.form["image_url"]
    }).execute()
    return redirect(url_for("admin"))

# Add sermon
@app.route("/admin/add-sermon", methods=["POST"])
def add_sermon():
    series_id = request.form["series_id"]
    supabase.table("sermons").insert({
        "title": request.form["title"],
        "date": request.form["date"],
        "speaker": request.form["speaker"],
        "topic": request.form["topic"],
        "book": request.form["book"],
        "audio_url": request.form["audio_url"],
        "image_url": request.form["image_url"],
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