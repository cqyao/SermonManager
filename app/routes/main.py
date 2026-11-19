from flask import Blueprint, render_template, current_app, request
from app.services import get_all_sermons_with_series, get_sermon_by_id, get_sermons_by_series
# Create the Blueprint instance
# 'auth' is the Blueprint's name; __name__ helps Flask locate resources
main_bp = Blueprint('main', __name__)

# Home page
@main_bp.route("/")
def index():
    sermons = get_all_sermons_with_series()
    return render_template("index.html", sermons=sermons)

# Individual series page
@main_bp.route("/series/<int:series_id>")
def series(series_id):
    supabase = current_app.extensions["supabase"]
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
@main_bp.route("/sermon/<int:sermon_id>")
@main_bp.route("/edit-sermon/<int:sermon_id>")
def sermon(sermon_id):
    sermon_data = get_sermon_by_id(sermon_id)
    
    if request.path.startswith("/edit-sermon/"):
        supabase = current_app.extensions["supabase"]
        speaker_response = supabase.table("unique_speakers").select("speaker").order("speaker").execute()
        return render_template(
            "edit-sermon.html",
            sermon=sermon_data,
            speakers=speaker_response.data or []
        )
    else: 
        sermons = get_sermons_by_series(sermon_data["series_id"])
        return render_template("sermon.html", sermon=sermon_data, sermons=sermons)



# All sermons
@main_bp.route("/sermons")
def sermons():
    supabase = current_app.extensions["supabase"]
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
    