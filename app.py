from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# All series
@app.route("/sermons")
def sermons():
    conn = get_db()
    sermons = conn.execute("""
        SELECT sermons.*, series.name as series_name, series.image_url
        FROM sermons
        LEFT JOIN series ON sermons.series_id = series.id
        ORDER BY sermons.date DESC
    """).fetchall()
    conn.close()
    return render_template("sermons.html", sermons=sermons)

# Individual series page
@app.route("/series/<int:series_id>")
def series(series_id):
    conn = get_db()
    series = conn.execute("SELECT * FROM series WHERE id = ?", (series_id,)).fetchone()
    sermons = conn.execute("""
        SELECT * FROM sermons
        WHERE series_id = ?
        ORDER BY date DESC
    """, (series_id,)).fetchall()
    conn.close()
    return render_template("series.html", series=series, sermons=sermons)

# Individual sermon page
@app.route("/sermon/<int:sermon_id>")
def sermon(sermon_id):
    conn = get_db()
    sermon = conn.execute("""
        SELECT sermons.*, series.name as series_name
        FROM sermons
        LEFT JOIN series ON sermons.series_id = series.id
        WHERE sermons.id = ?
    """, (sermon_id,)).fetchone()
    conn.close()
    return render_template("sermon.html", sermon=sermon)
  
@app.route("/admin")
def admin():
    conn = get_db()
    sermons = conn.execute("""
        SELECT sermons.*, series.name as series_name
        FROM sermons
        LEFT JOIN series ON sermons.series_id = series.id
        ORDER BY sermons.date DESC
    """).fetchall()
    series = conn.execute("SELECT * FROM series").fetchall()
    conn.close()
    return render_template("admin.html", sermons=sermons, series=series)

@app.route("/admin/add-series", methods=["POST"])
def add_series():
    name = request.form["name"]
    image_url = request.form["image_url"]
    conn = get_db()
    conn.execute("INSERT INTO series (name, image_url) VALUES (?, ?)", (name, image_url))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/admin/add-sermon", methods=["POST"])
def add_sermon():
    conn = get_db()
    conn.execute("""
        INSERT INTO sermons (title, date, speaker, topic, book, audio_url, image_url, series_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["title"],
        request.form["date"],
        request.form["speaker"],
        request.form["topic"],
        request.form["book"],
        request.form["audio_url"],
        request.form["image_url"],
        request.form["series_id"] or None
    ))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/admin/delete-sermon/<int:sermon_id>", methods=["POST"])
def delete_sermon(sermon_id):
    conn = get_db()
    conn.execute("DELETE FROM sermons WHERE id = ?", (sermon_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)



def get_db():
    conn = sqlite3.connect("sermons.db")
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image_url TEXT
        );
                       
        CREATE TABLE IF NOT EXISTS sermons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            speaker TEXT,
            topic TEXT,
            book TEXT,
            audio_url TEXT,
            series_id INTEGER,
            FOREIGN KEY (series_id) REFERENCES series(id)
        );
    """)
    conn.commit()
    conn.close()
    
def migrate_db():
  conn = get_db()
  conn.execute("ALTER TABLE sermons ADD COLUMN image_url TEXT")
  conn.commit()
  conn.close()
  

    
init_db()