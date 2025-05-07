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
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form.get('remarks')  # Optional
        follow_up_date = request.form.get('follow_up_date')  # Get the follow-up date (optional)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patients (uhid, name, age, sex, remarks, follow_up_date)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (uhid, name, age, sex, remarks, follow_up_date))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        else:
            return "Error connecting to database."

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
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE uhid = %s;", (uhid,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        else:
            return "Error connecting to database."
    except Exception as e:
        return f"An error occurred: {e}"


    
@app.route('/follow_up', methods=['GET', 'POST'])
def follow_up():
    if request.method == 'POST':
        uhid = request.form['uhid']
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        remarks = request.form['remarks']
        follow_up_date = request.form['follow_up_date']  # Get the follow-up date

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # Check if patient exists
            cursor.execute("SELECT * FROM patients WHERE uhid = %s", (uhid,))
            patient = cursor.fetchone()

            if patient:
                # If patient exists, update with follow-up date
                cursor.execute("""
                    UPDATE patients
                    SET name = %s, age = %s, sex = %s, remarks = %s, follow_up_date = %s
                    WHERE uhid = %s
                """, (name, age, sex, remarks, follow_up_date, uhid))
            else:
                # If patient doesn't exist, insert as new patient
                cursor.execute("""
                    INSERT INTO patients (uhid, name, age, sex, remarks, follow_up_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (uhid, name, age, sex, remarks, follow_up_date))

            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))

        else:
            return "Error connecting to database."

    return render_template('followup.html')





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



if __name__ == '__main__':
    app.run(debug=True)
