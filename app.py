from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import urllib.parse as up
import os

up.uses_netloc.append("postgres")
url = up.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

@app.route('/')
def index():
    return "App is running!"

@app.route('/submit_sighting', methods=['POST'])
def submit_sighting():
    data = request.json
    species = data['species']
    notes = data.get('notes', '')
    lat, lng = map(float, data['location'].split(','))

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO wildlife_sightings (species, notes, location)
            VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (species, notes, lng, lat))
        conn.commit()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)