from flask import Blueprint, render_template, url_for, request, current_app, jsonify, redirect, flash
from flask_login import login_required
from app.services import get_all_sermons_with_series, get_available_images, handle_image_upload
from ..forms import AddSermonForm


admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin")
@login_required
def admin():
    supabase = current_app.extensions["supabase"]
    sermons = get_all_sermons_with_series()
    series_response = supabase.table("series").select("*").execute()
    series = series_response.data
    return render_template("admin.html", sermons=sermons, series=series)

@admin_bp.route("/add-sermon")
@login_required
def add_new_sermon():
    supabase = current_app.extensions["supabase"]
    images = get_available_images()
    form = AddSermonForm()
    series_response = supabase.table("series").select("*").execute()
    series = series_response.data
    form.series_id.choices = [(0, "-- Select A Series -- ", {'disabled': True})] + [(s["id"], s["name"]) for s in series]
    return render_template("add-sermon.html", images=images, form=form)

@admin_bp.route("/all-sermon")
@login_required
def all_sermon():
    sermons = get_all_sermons_with_series()
    return render_template("all-sermon.html", sermons=sermons)

# Submit edits to an existing sermon
@admin_bp.route("/admin/edit-sermon/<int:sermon_id>", methods=["POST"])
@login_required
def edit_sermon(sermon_id):
    supabase = current_app.extensions["supabase"]
    series_id = request.form["series_id"]

    supabase.table("sermons").update({
        "title": request.form["Title"],
        "date": request.form["Date"],
        "speaker": request.form["Speaker"],
        "topic": request.form["Topic"],
        "book": request.form["Book"],
        "audio_url": request.form["AudioURL"],
        "series_id": int(series_id) if series_id else None
    }).eq("id", sermon_id).execute()
    return redirect(url_for("admin.all_sermon"))

# Add sermon to the database
@admin_bp.route("/admin/add-sermon", methods=["POST"])
@login_required
def add_sermon():
    form = AddSermonForm()
    image_url = handle_image_upload()
    if form.validate_on_submit():
        supabase = current_app.extensions["supabase"]
        image_url = handle_image_upload()
        series_id = request.form["series_id"]
        supabase.table("sermons").insert({
            "title": form.title.data,
            "date": form.date.data,
            "speaker": form.speaker.data,
            "topic": form.topic.data,
            "book": form.book.data,
            "audio_url": form.audio_url.data,
            "image_url": image_url,
            "series_id": int(series_id) if series_id else None
        }).execute()
        return redirect(url_for("admin.all_sermon"))

# Delete sermon from the database
@admin_bp.route("/admin/delete-sermon/<int:sermon_id>", methods=["POST"])
@login_required
def delete_sermon(sermon_id):
    supabase = current_app.extensions["supabase"]
    supabase.table("sermons").delete().eq("id", sermon_id).execute()
    flash("Sermon deleted successfully.")
    return redirect(url_for("admin.all_sermon"))

# Add a series to the database
@admin_bp.route("/admin/add-series", methods=["POST"])
@login_required
def add_series():
    supabase = current_app.extensions["supabase"]
    wants_json = request.accept_mimetypes.best == "application/json"
    series_name = request.form.get("SeriesName", "").strip()
    if not series_name:
        if wants_json:
            return jsonify(error="Enter a name for the new series."), 400
        flash("Enter a name for the new series.", "error")
        return redirect(url_for("admin.add_new_sermon"))

    response = supabase.table("series").insert({
        "name": series_name
    }).select("id, name").execute()
    if not response.data:
        raise RuntimeError("The new series was not returned after insertion.")

    if wants_json:
        return jsonify(series=response.data[0])

    flash(f'Series "{series_name}" added.', "success")
    return redirect(url_for("admin.add_new_sermon"))