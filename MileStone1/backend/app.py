from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

# Database connection
def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.route('/models', methods=['GET'])
def get_models():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM models;")
    models = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(models)

if __name__ == '__main__':
    app.run(debug=True)
