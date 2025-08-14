from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
import urllib.parse as up
import os
import json

app = Flask(__name__)
CORS(app)

# Load environment variables
up.uses_netloc.append("postgres")
url = up.urlparse(os.environ["DATABASE_URL"])

# Connect to PostgreSQL
conn = psycopg2.connect(
    database=url.path[1:],        
    user=url.username,            
    password=url.password,         
    host=url.hostname,             
    port=url.port                  
)

wildlife_conn = psycopg2.connect(
    dbname="wildlife_map",
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

# Serve frontend
@app.route('/')
def index():
    return render_template('index.html')

# Wildlife form submission
@app.route('/submit_sighting', methods=['POST'])
def submit_sighting():
    try:
        data = request.json
        species = data['species']
        notes = data.get('notes', '')
        lat, lng = map(float, data['location'].split(','))

        with wildlife_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO wildlife_sightings (species, notes, location)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            """, (species, notes, lng, lat))
            conn.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        conn.rollback()
        print("Wildlife form error:", e)  # This will show the real error in your terminal
        return jsonify({'error': str(e)}), 500

# Campsites API
@app.route('/api/campsites')
def get_campsites():
    return fetch_geojson("public.campsites", [
        "popup_desc", "website_url", "site_type", "amenities"
    ])

# Parking API
@app.route('/api/parking')
def get_parking():
    return fetch_geojson("public.parking", ["name"])

# Trailheads API
@app.route('/api/trailheads')
def get_trailheads():
    return fetch_geojson("public.trailheads", [
        "trail_name", "description", "difficulty", "length"
    ])

# Wineries API
@app.route('/api/wineries')
def get_wineries():
    return fetch_geojson("public.wineries", [
        "name", "address", "website_url"
    ])

# Generic GeoJSON fetcher
def fetch_geojson(table, columns):
    try:
        with conn.cursor() as cur:
            col_str = ", ".join(columns)
            cur.execute(f"""
                SELECT {col_str}, ST_AsGeoJSON(wkb_geometry) AS geometry
                FROM {table}
                WHERE wkb_geometry IS NOT NULL
            """)
            rows = cur.fetchall()

        features = []
        for row in rows:
            *props, geometry = row
            try:
                geojson = json.loads(geometry)
            except Exception as geo_err:
                print(f"GeoJSON parse error ({table}): {geo_err}")
                continue

            features.append({
                "type": "Feature",
                "geometry": geojson,
                "properties": dict(zip(columns, props))
            })

        return jsonify({"type": "FeatureCollection", "features": features})

    except Exception as e:
        conn.rollback()
        print(f"Error in /api/{table}: {e}")
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)