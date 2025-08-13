from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
import urllib.parse as up
import os

app = Flask(__name__)
CORS(app)

# Parse database URL from environment
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

# Serve frontend
@app.route('/')
def index():
    return render_template('index.html')

# Wildlife form submission
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

# Optional generic submit route (if needed)
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    # process and store data
    return jsonify({'status': 'success'})

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)