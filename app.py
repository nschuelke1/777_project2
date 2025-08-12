from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="wildlife_map",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)

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
    app.run(debug=True)