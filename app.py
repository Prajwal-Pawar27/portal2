import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

# Initialize Flask app
app = Flask(__name__)
app.debug = True

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
        print(f"Fetched Patients: {patients}")  # Debugging line
        cursor.close()
        conn.close()
        return render_template('index.html', patients=patients)
    else:
        return "Error connecting to database."


@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        # Get the data from the form
        uhid = request.form['uhid']  # Capture the UHID
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']
        follow_up_date = request.form['follow_up_date']

        # Ensure UHID is provided (can be validated further if needed)
        if not uhid:
            return "Error: UHID is required."

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert patient into the database with UHID included
        cursor.execute("""
            INSERT INTO patients (uhid, name, age, sex, remarks, follow_up_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (uhid, name, age, sex, remarks, follow_up_date))

        conn.commit()
        cursor.close()
        conn.close()

        # Redirect to the home page after successful patient addition
        return redirect(url_for('home'))

    return render_template('new.html')




@app.route('/edit_patient/<uhid>', methods=['GET', 'POST'])
def edit_patient(uhid):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE uhid = %s;", (uhid,))
        patient = cursor.fetchone()

        if not patient:
            return "Patient not found."

        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            sex = request.form['sex']
            remarks = request.form['remarks']

            print(f"Updating patient {uhid} with data: Name={name}, Age={age}, Sex={sex}, Remarks={remarks}")

            cursor.execute("""
                UPDATE patients
                SET name = %s, age = %s, sex = %s, remarks = %s
                WHERE uhid = %s;
            """, (name, age, sex, remarks, uhid))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

        cursor.close()
        conn.close()
        return render_template('edit.html', patient=patient)
    else:
        return "Error connecting to database."


@app.route('/delete_patient/<uhid>', methods=['POST'])
def delete_patient(uhid):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE uhid = %s", (uhid,))
        conn.commit()
        cursor.close()
        conn.close()
        
        # After deletion, redirect to the patient information page
        return redirect(url_for('patient_info'))  # Stay on the patient info page after deletion

    return "Error connecting to database."



@app.route('/follow_up/<uhid>', methods=['GET', 'POST'])
def follow_up_patient(uhid):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE uhid = %s", (uhid,))
        patient = cursor.fetchone()

        if request.method == 'POST':
            diagnosis = request.form['diagnosis']
            follow_up_date = request.form.get('follow_up_date')  # .get() for safety
            remarks = request.form.get('remarks')  # Capture remarks

            if not follow_up_date:
                return "Error: Follow Up Date is required."

            cursor.execute("""
                UPDATE patients SET diagnosis = %s, follow_up_date = %s, remarks = %s
                WHERE uhid = %s
            """, (diagnosis, follow_up_date, remarks, uhid))

            conn.commit()

            # After updating, fetch the updated data
            cursor.execute("SELECT * FROM patients WHERE uhid = %s", (uhid,))
            updated_patient = cursor.fetchone()

            cursor.close()
            conn.close()

            # Redirect to the home page after successful follow-up update
            return redirect(url_for('home'))

        return render_template('followup.html', patient=patient)
    else:
        return "Error connecting to database."


@app.route('/patient_info', methods=['GET'])
def patient_info():
    query = request.args.get('search', '')
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        if query:
            cursor.execute("""
                SELECT * FROM patients
                WHERE uhid ILIKE %s OR name ILIKE %s;
            """, (f'%{query}%', f'%{query}%'))
        else:
            cursor.execute("SELECT * FROM patients;")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('patients.html', patients=patients, query=query)
    else:
        return "Error connecting to database."


@app.route('/patient_action', methods=['POST'])
def patient_action():
    visit_type = request.form['visit']
    if visit_type == 'new_patient':
        return redirect(url_for('new_patient'))
    elif visit_type == 'follow_up':
        # Ensure that you pass a valid `uhid` to follow_up_patient
        uhid = request.form['uhid']  # Or get from some other source
        return redirect(url_for('follow_up_patient', uhid=uhid))
    else:
        return "Invalid action"

@app.route('/')
def home():
    return render_template('index.html')



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
