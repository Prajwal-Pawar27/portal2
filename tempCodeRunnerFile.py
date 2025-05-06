from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# --- Helper to get DB connection ---
def get_db_connection():
    conn = sqlite3.connect('patients.db')
    conn.row_factory = sqlite3.Row
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
        conn.execute("INSERT INTO patients (uhid, name, age, sex, remarks) VALUES (?, ?, ?, ?, ?)",
                     (uhid, name, age, sex, remarks))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('new.html')

# --- Follow-Up (Same as adding a new patient entry) ---
@app.route('/followup', methods=['GET', 'POST'])
def follow_up():
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']

        conn = get_db_connection()
        conn.execute("INSERT INTO patients (uhid, name, age, sex, remarks) VALUES (?, ?, ?, ?, ?)",
                     (uhid, name, age, sex, remarks))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('followup.html')

# --- View Patients (with optional search) ---
@app.route('/patients')
def patient_info():
    query = request.args.get('search', '')
    conn = get_db_connection()
    if query:
        patients = conn.execute("SELECT * FROM patients WHERE name LIKE ? OR uhid LIKE ?", 
                                ('%' + query + '%', '%' + query + '%')).fetchall()
    else:
        patients = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
    conn.close()
    return render_template('patients.html', patients=patients, query=query)

# --- Edit Patient ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = get_db_connection()
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']
        conn.execute("UPDATE patients SET uhid=?, name=?, age=?, sex=?, remarks=? WHERE id=?",
                     (uhid, name, age, sex, remarks, id))
        conn.commit()
        conn.close()
        return redirect(url_for('patient_info'))

    patient = conn.execute("SELECT * FROM patients WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit.html', patient=patient)

# --- Delete Patient ---
@app.route('/delete/<int:id>')
def delete_patient(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.execute("DELETE FROM sqlite_sequence WHERE name='patients'")
    conn.commit()
    conn.close()
    return redirect(url_for('patient_info'))

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
