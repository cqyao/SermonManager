from flask import current_app, request
import uuid


def _get_supabase():
    return current_app.extensions["supabase"]

def get_all_sermons_with_series():
    supabase = _get_supabase()
    return (
        supabase.table("sermons")
        .select("*, series:series_id(name)")
        .execute()
        .data
    )

def get_available_images():
    """Returns list of public URLs for all available images"""
    images = []
    supabase = _get_supabase()
    image_metadata = supabase.storage.from_("images").list()
    for filename in image_metadata:
        image_url = supabase.storage.from_("images").get_public_url(filename['name'])
        images.append(image_url)
    return images

def handle_image_upload(form_field_name="image"):
    """
    Handles image upload from form or selected existing image.
    Returns the image URL or None if no image provided.
    """
    image_url = None
    supabase = _get_supabase()
    
    # First, check if user selected an existing image
    selected_image_url = request.form.get("selected_image_url", "").strip()
    if selected_image_url:
        image_url = selected_image_url
    # Otherwise, handle uploading a new image if provided
    elif form_field_name in request.files:
        file = request.files[form_field_name]
        if file.filename != "":
            extension = file.filename.rsplit(".", 1)[-1]
            filename = f"{uuid.uuid4()}.{extension}"
            
            supabase.storage.from_("images").upload(
                path=filename,
                file=file.read(),
                file_options={"content-type": file.content_type}
            )
            image_url = supabase.storage.from_("images").get_public_url(filename)
    
    return image_url

def get_sermon_by_id(sermon_id):
    """Fetches a single sermon with series info"""
    supabase = _get_supabase()
    response = supabase.table("sermons") \
        .select("*, series:series_id(name)") \
        .eq("id", sermon_id) \
        .single() \
        .execute()
    return response.data

def get_sermons_by_series(series_id):
    """Returns all sermons from a particular series, ordered by date (newest first)"""
    if series_id is None:
        return []
    supabase = _get_supabase()
    response = supabase.table("sermons") \
        .select("*") \
        .eq("series_id", series_id) \
        .order("date", desc=True) \
        .execute()
    return response.data or []
