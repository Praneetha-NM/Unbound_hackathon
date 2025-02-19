from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Database connection
def connect_db():
    try:
        return psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    except psycopg2.Error as e:
        print("Database connection error:", e)
        return None


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
