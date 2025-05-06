import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Use the external DATABASE_URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://patient_db_lukp_user:0uQieJtukroY5HldFbHvDNrGAAt5pH3r@dpg-d0d3ce24d50c73edp4o0-a.singapore-postgres.render.com/patient_db_lukp')

# --- Helper to get DB connection ---
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# --- Home Page ---
@app.route('/')
def home():
    return render_template('index.html', consultants="Dr. Y.S. Pawar & Dr. Manjula")


# --- Add New Patient ---
@app.route('/new', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']

        conn = get_db_connection()
        cursor = conn.cursor()  # Create cursor to execute queries
        cursor.execute("INSERT INTO patients (uhid, name, age, sex, remarks) VALUES (%s, %s, %s, %s, %s)",
                       (uhid, name, age, sex, remarks))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('new.html')

# --- Follow-Up ---
@app.route('/followup', methods=['GET', 'POST'])
def follow_up():
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']

        conn = get_db_connection()
        cursor = conn.cursor()  # Create cursor to execute queries
        cursor.execute("INSERT INTO patients (uhid, name, age, sex, remarks) VALUES (%s, %s, %s, %s, %s)",
                       (uhid, name, age, sex, remarks))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('followup.html')

# --- View Patients ---
@app.route('/patients')
def patient_info():
    query = request.args.get('search', '')
    conn = get_db_connection()
    cursor = conn.cursor()  # Create cursor to execute queries
    if query:
        cursor.execute("SELECT * FROM patients WHERE name LIKE %s OR uhid LIKE %s", 
                       ('%' + query + '%', '%' + query + '%'))
    else:
        cursor.execute("SELECT * FROM patients ORDER BY name")
    patients = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients, query=query)

# --- Edit Patient ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor()  # Create cursor to execute queries
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']
        cursor.execute("UPDATE patients SET uhid=%s, name=%s, age=%s, sex=%s, remarks=%s WHERE id=%s",
                       (uhid, name, age, sex, remarks, id))
        conn.commit()
        conn.close()
        return redirect(url_for('patient_info'))

    cursor.execute("SELECT * FROM patients WHERE id=%s", (id,))
    patient = cursor.fetchone()
    conn.close()
    return render_template('edit.html', patient=patient)

# --- Delete Patient ---
@app.route('/delete/<int:id>')
def delete_patient(id):
    conn = get_db_connection()
    cursor = conn.cursor()  # Create cursor to execute queries
    cursor.execute("DELETE FROM patients WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('patient_info'))

# --- Initialize DB ---
@app.route('/init')
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            uhid VARCHAR(50),
            name VARCHAR(100),
            age INTEGER,
            sex VARCHAR(10),
            remarks TEXT
        )
    ''')
    conn.commit()
    conn.close()
    return "Database initialized!"

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
