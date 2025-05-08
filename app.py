import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)
app.debug = True

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Missing one or more environment variables for DB connection.")

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
    return render_template('index.html')

@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        uhid = request.form.get('uhid')
        name = request.form.get('name')
        age = request.form.get('age')
        sex = request.form.get('sex')
        remarks = request.form.get('remarks')
        follow_up_date = request.form.get('follow_up_date')
        diagnosis = request.form.get('diagnosis')

        if not uhid or not name or not age:
            return "Error: UHID, Name, and Age are required."

        conn = get_db_connection()
        if not conn:
            return "Error connecting to database."
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO patients (uhid, name, age, sex, remarks, follow_up_date, diagnosis)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (uhid, name, age, sex, remarks, follow_up_date, diagnosis))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('index'))

    return render_template('new.html')

@app.route('/edit_patient/<uhid>', methods=['GET', 'POST'])
def edit_patient(uhid):
    conn = get_db_connection()
    if not conn:
        return "Error connecting to database."
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE uhid = %s;", (uhid,))
    patient = cursor.fetchone()

    if not patient:
        cursor.close()
        conn.close()
        return "Patient not found."

    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        sex = request.form.get('sex')
        remarks = request.form.get('remarks')
        diagnosis = request.form.get('diagnosis')

        cursor.execute("""
            UPDATE patients
            SET name = %s, age = %s, sex = %s, remarks = %s, diagnosis = %s
            WHERE uhid = %s;
        """, (name, age, sex, remarks, diagnosis, uhid))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('patient_info'))

    cursor.close()
    conn.close()
    return render_template('edit.html', patient=patient)

@app.route('/delete_patient/<uhid>', methods=['POST'])
def delete_patient(uhid):
    conn = get_db_connection()
    if not conn:
        return "Error connecting to database."
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE uhid = %s;", (uhid,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('patient_info'))

@app.route('/follow_up/<uhid>', methods=['GET', 'POST'])
def follow_up_patient(uhid):
    conn = get_db_connection()
    if not conn:
        return "Error connecting to database."
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE uhid = %s;", (uhid,))
    patient = cursor.fetchone()

    if not patient:
        cursor.close()
        conn.close()
        return "Patient not found."

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        follow_up_date = request.form.get('follow_up_date')
        remarks = request.form.get('remarks')

        if not follow_up_date:
            return "Error: Follow Up Date is required."

        cursor.execute("""
            UPDATE patients
            SET diagnosis = %s, follow_up_date = %s, remarks = %s
            WHERE uhid = %s;
        """, (diagnosis, follow_up_date, remarks, uhid))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('patient_info'))

    cursor.close()
    conn.close()
    return render_template('followup.html', patient=patient)

@app.route('/patient_info', methods=['GET'])
def patient_info():
    query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    if page < 1:
        return redirect(url_for('patient_info', page=1))

    per_page = 50
    offset = (page - 1) * per_page

    conn = get_db_connection()
    if not conn:
        return "Error connecting to database."
    cursor = conn.cursor()

    if query:
        cursor.execute("""
            SELECT * FROM patients
            WHERE uhid ILIKE %s OR name ILIKE %s
            ORDER BY id
            LIMIT %s OFFSET %s;
        """, (f'%{query}%', f'%{query}%', per_page, offset))
        patients = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) FROM patients
            WHERE uhid ILIKE %s OR name ILIKE %s;
        """, (f'%{query}%', f'%{query}%'))
        count_result = cursor.fetchone()
    else:
        cursor.execute("SELECT * FROM patients ORDER BY id LIMIT %s OFFSET %s;", (per_page, offset))
        patients = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM patients;")
        count_result = cursor.fetchone()

    total_patients = count_result[0] if count_result else 0
    total_pages = (total_patients + per_page - 1) // per_page

    if page > total_pages and total_pages != 0:
        cursor.close()
        conn.close()
        return redirect(url_for('patient_info', page=total_pages, search=query))

    cursor.close()
    conn.close()

    return render_template(
        'patients.html',
        patients=patients,
        query=query,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@app.route('/patient_action', methods=['POST'])
def patient_action():
    visit_type = request.form.get('visit')
    if visit_type == 'new_patient':
        return redirect(url_for('new_patient'))
    elif visit_type == 'follow_up':
        uhid = request.form.get('uhid')
        if not uhid:
            return "Error: UHID is required for follow-up."
        return redirect(url_for('follow_up_patient', uhid=uhid))
    else:
        return "Invalid action"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
