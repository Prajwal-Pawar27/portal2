from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# --- PostgreSQL connection details ---
DB_HOST = "localhost"
DB_NAME = "patient_db"
DB_USER = "postgres"
DB_PASS = "Prajwal@123"

# --- Helper to get DB connection ---
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
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
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patients (uhid, name, age, sex, remarks) VALUES (%s, %s, %s, %s, %s)",
            (uhid, name, age, sex, remarks)
        )
        conn.commit()
        cur.close()
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
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patients (uhid, name, age, sex, remarks) VALUES (%s, %s, %s, %s, %s)",
            (uhid, name, age, sex, remarks)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('home'))
    return render_template('followup.html')

# --- View Patients ---
@app.route('/patients')
def patient_info():
    query = request.args.get('search', '')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if query:
        cur.execute(
            "SELECT * FROM patients WHERE name ILIKE %s OR uhid ILIKE %s ORDER BY name",
            (f'%{query}%', f'%{query}%')
        )
    else:
        cur.execute("SELECT * FROM patients ORDER BY name")
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('patients.html', patients=patients, query=query)

# --- Edit Patient ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']
        cur.execute(
            "UPDATE patients SET uhid=%s, name=%s, age=%s, sex=%s, remarks=%s WHERE id=%s",
            (uhid, name, age, sex, remarks, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('patient_info'))

    cur.execute("SELECT * FROM patients WHERE id=%s", (id,))
    patient = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', patient=patient)

# --- Delete Patient ---
@app.route('/delete/<int:id>')
def delete_patient(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('patient_info'))

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
