import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

# Initialize Flask app
app = Flask(__name__)

# Fetch database credentials from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Check if the required environment variables are set
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("One or more environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD) are missing")

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients;")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', patients=patients)
    else:
        return "Error connecting to database."

@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        contact = request.form['contact']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patients (name, age, gender, address, contact)
                VALUES (%s, %s, %s, %s, %s);
            """, (name, age, gender, address, contact))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        else:
            return "Error connecting to database."

    return render_template('new_patient.html')

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = %s;", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            return "Patient not found."

        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            gender = request.form['gender']
            address = request.form['address']
            contact = request.form['contact']

            cursor.execute("""
                UPDATE patients
                SET name = %s, age = %s, gender = %s, address = %s, contact = %s
                WHERE id = %s;
            """, (name, age, gender, address, contact, patient_id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

        cursor.close()
        conn.close()
        return render_template('edit_patient.html', patient=patient)
    else:
        return "Error connecting to database."

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = %s;", (patient_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    else:
        return "Error connecting to database."

if __name__ == '__main__':
    app.run(debug=True)
