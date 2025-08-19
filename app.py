from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import json

app = Flask(__name__, static_folder='static')
CORS(app)

# Wildlife DB connection
wildlife_conn = psycopg2.connect(
    dbname="wildlife_map",
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"]
)

@app.route('/')
def index():
    return render_template('index.html')

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
            wildlife_conn.commit()

        return jsonify({'status': 'success'})

    except Exception as e:
        wildlife_conn.rollback()
        print("Wildlife form error:", e)
        return jsonify({'error': str(e)}), 500

# Serve static GeoJSON files
@app.route('/data/<filename>')
def serve_geojson(filename):
    try:
        with open(os.path.join(app.static_folder, 'data', filename)) as f:
            geojson = json.load(f)
        return jsonify(geojson)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)