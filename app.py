from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = mysql.connector.connect(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'employee'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')

@app.route("/student")
def student():
    return render_template('student.html')

# ------------------------------------
# |             STUDENT              |
# ------------------------------------
# Route to student login page
@app.route("/studentLoginPage")
def studentLoginPage(msg=""):
    return render_template('studentLogin.html', msg=msg)
    
# Route to student main page
@app.route("/student/<id>", methods=['GET'])
def student(id):
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE id = %s', (id,))
    account = cursor.fetchone()
    cursor.execute('SELECT * FROM supervisor')
    supervisor = cursor.fetchall()
    
    # Get the success message from the query parameters
    success_message = request.args.get('success_message', None)

    return render_template('student.html', account=account, supervisors=supervisor, success_message=success_message)

# Route to student profile page
@app.route("/studentProfile/<student_id>")
def studentProfile(student_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        cursor.execute('SELECT * FROM student WHERE id = %s', (student_id,))
        account = cursor.fetchone()

        cursor.execute('SELECT * FROM supervisor WHERE id = %s', (account[9],))
        supervisor = cursor.fetchone() 
    finally:
        cursor.close()

    print(account[0])
    return render_template('studentProfile.html', student=account, supervisor=supervisor)

# Student login function
@app.route("/studentLogin", methods=['GET'])
def studentLogin():
    id = request.args.get('id')
    password = request.args.get('password')

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE id = %s', (id,))
    account = cursor.fetchone()

    if account:
        if password == account[4]:
            return redirect(url_for('student', id=id))
        else:
            msg = 'Account exists but password incorrect'
            return redirect(url_for('studentLogin', msg=msg))
    else:
        msg = 'Account does not exist'
        return redirect(url_for('studentLogin', msg=msg))

# Select supervisor function
@app.route("/select-supervisor", methods=['POST'])
def selectSupervisor():
    id = request.form['id']
    supervisor = request.form['supervisor']
    cursor = db_conn.cursor()
    cursor.execute('UPDATE student SET supervisor_id = %s WHERE id = %s', (supervisor, id))
    db_conn.commit()
    
    # Set a success message
    success_message = "Supervisor selection was successful!"
    
    # Redirect to the student page with the success message as a query parameter
    return redirect(url_for('student', id=id, success_message=success_message))

# Student edit profile function
@app.route("/editStudentProfile/<student_id>")
def editStudentProfile(student_id):
    # Get user input name, email and phone number from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        cursor.execute('UPDATE student SET name = %s, email = %s, phone_number = %s WHERE id = %s', (name, email, phone, student_id))
        db_conn.commit()

    finally:
        cursor.close()

    return redirect(url_for('studentProfile', student_id=student_id))


# Student logout function
@app.route("/studentLogout")
def studentLogout():
    return redirect(url_for('studentLoginPage'))

# ------------------------------------
# |            SUPERVISOR            |
# ------------------------------------  
# Route to supervisor login page
@app.route("/supervisorLoginPage")
def supervisorLoginPage(msg=""):
    return render_template('supervisorLogin.html', msg=msg)

# Route to supervisor main page
@app.route("/supervisorMain/<id>")
def supervisorMain(id):
    print("id",id)
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE supervisor_id = %s', (id,))
    students = cursor.fetchall()

    cursor.execute('SELECT * FROM supervisor WHERE id = %s', (id,))
    account = cursor.fetchone()
    print("account",account)
    print("students",students)
    return render_template('supervisorMain.html', students=students, supervisor=account)

# Route to supervisor evaluation page
@app.route("/evaluatePage/<id>")
def evaluatePage(id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM student WHERE id = %s", (id,))
    students = cursor.fetchall()
    return render_template('supervisorEvaluate.html' , students=students)

# Supervisor login function
@app.route("/supervisorLogin" , methods=['GET'])
def supervisorLogin():
    id = request.args.get('id')
    password = request.args.get('password')

    print("id",id)
    print("pw",password)

    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM supervisor WHERE id = %s', (id,))
    account = cursor.fetchone()

    if account:
        if password == account[1]:
            return redirect(url_for('supervisorMain', id=account[0]))
        else:
            msg = 'Account exists but password incorrect'
            return redirect(url_for('supervisorLogin', msg=msg))
    else:
        msg = 'Account does not exist'
        return redirect(url_for('supervisorLogin', msg=msg))
    
# Supervisor evaluate function
@app.route("/submit_evaluation", methods=['POST'])
def submitEvaluation():
    student_id = request.form['student_id']
    supervisor_id = request.form['supervisor_id']
    communication_skills = request.form['communication_skills']
    technical_skills = request.form['technical_skills']
    problem_solving = request.form['problem_solving']
    comments = request.form['comments']

    insert_sql = "INSERT INTO evaluation VALUES (%s, %s, %s, %s, %s)"

    # update the isEvaluated field in student table
    update_sql = "UPDATE student SET isEvaluated = 1 WHERE id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (student_id, communication_skills, technical_skills, problem_solving, comments))
        cursor.execute(update_sql, (student_id,))
        db_conn.commit()
    finally:
        cursor.close()

    print("supervisor_id",supervisor_id)
    print("student_id",student_id)
    print("communication_skills",communication_skills)
    print("technical_skills",technical_skills)
    print("problem_solving",problem_solving)
    print("comments",comments)
    return redirect(url_for('supervisorMain', id=supervisor_id))

# Supervisor edit profile function
@app.route("/editSupervisorProfile/<supervisor_id>")
def editSupervisorProfile(supervisor_id):
    print(supervisor_id)

    # Get user input name, email and phone number from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update admin data in database
        cursor.execute('UPDATE supervisor SET name = %s, email = %s, phone_number = %s WHERE id = %s', (name, email, phone, supervisor_id))
        db_conn.commit()

        # Get admin data from database
        cursor.execute('SELECT * FROM supervisor WHERE id = %s', (supervisor_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    return redirect(url_for('supervisorProfile', supervisor_id=supervisor_id, supervisor=account))

# Supervisor logout function
@app.route("/supervisorLogout")
def supervisorLogout():
    return redirect(url_for('supervisorLoginPage'))

# -------------------------------
# |           ADMIN             |
# -------------------------------
# Route to admin login page
@app.route("/adminLogin")
def adminLogin(msg=""):
    return render_template('adminLogin.html', msg=msg)

# Route to admin profile page
@app.route("/adminProfile/<admin_id>")
def adminProfile(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get admin data from database
        cursor.execute('SELECT * FROM admin WHERE id = %s', (admin_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    print(account[0])

    return render_template('adminProfile.html', admin_id=admin_id, account=account)

# Route to company list page
@app.route("/admin/<admin_id>/companyList", methods=['GET'])
def companyList(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get all company data from database
        cursor.execute('SELECT * FROM company')
        companies = cursor.fetchall()
    finally:
        cursor.close()

    print(companies)

    return render_template('companyList.html', companies=companies, admin_id=admin_id)

# Route to supervisor list page
@app.route("/admin/<admin_id>/supervisorList", methods=['GET'])
def supervisorList(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get all supervisor data from database
        cursor.execute('SELECT * FROM supervisor')
        supervisors = cursor.fetchall()
    finally:
        cursor.close()

    return render_template('supervisorList.html', supervisors=supervisors, admin_id=admin_id)

# Route to add supervisor page
@app.route("/admin/<admin_id>/addSupervisor", methods=['GET'])
def addSupervisor(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get last supervisor id from database
        cursor.execute('SELECT id FROM supervisor ORDER BY id DESC LIMIT 1')
        last_supervisor_id = cursor.fetchone()
    finally:
        cursor.close()

    # Change tuple to integer
    last_supervisor_id = int(last_supervisor_id[0])

    # Increment last supervisor id by 1
    new_supervisor_id = last_supervisor_id + 1

    # Change integer back to six character string
    new_supervisor_id = str(new_supervisor_id).zfill(6)

    return render_template('addSupervisor.html', admin_id=admin_id, new_supervisor_id=new_supervisor_id)

# Admin edit profile function
@app.route("/editProfile/<admin_id>")
def editProfile(admin_id):
    # Get user input name, email and phone number from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update admin data in database
        cursor.execute('UPDATE admin SET name = %s, email = %s, phone_number = %s WHERE id = %s', (name, email, phone, admin_id))
        db_conn.commit()
    finally:
        cursor.close()

    return redirect(url_for('adminProfile', admin_id=admin_id))

# Admin login function
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Get user input email and password from HTML form
    admin_id = request.args.get('admin_id')
    password = request.args.get('password')

    # Connect to MySQL database
    cursor = db_conn.cursor()
    
    try:
        # Check if email exists in accounts table in out database
        cursor.execute('SELECT * FROM admin WHERE id = %s', (admin_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    # If account exists in accounts table in out database
    if account:
        # Check if password correct
        if password == account[4]:
            # If password correct, redirect to admin page
            return redirect(url_for('adminProfile', admin_id=admin_id))
        else:
            # If password incorrect, redirect to admin login page with error message
            msg = 'Account exists but password incorrect'
            return render_template('adminLogin.html', msg=msg)
    # If account not exists in accounts table in out database
    else:
        msg = 'Account does not exists'
        return render_template('adminLogin.html', msg=msg)
    
# Admin logout function
@app.route("/adminLogout")
def adminLogout():
    return redirect(url_for('adminLogin'))

# Admin accept company function
@app.route("/<admin_id>/acceptCompany/<company_id>")
def acceptCompany(admin_id, company_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update company status in database
        cursor.execute('UPDATE company SET status = %s, isReviewed = 1 WHERE id = %s', ('ACCEPTED', company_id))
        db_conn.commit()

        # Get all company data from database
        cursor.execute('SELECT * FROM company')
        companies = cursor.fetchall()
    finally:
        cursor.close()

    return redirect(url_for('companyList', admin_id=admin_id))

# Admin reject company function
@app.route("/<admin_id>/rejectCompany/<company_id>")
def rejectCompany(admin_id, company_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update company status in database
        cursor.execute('UPDATE company SET status = %s, isReviewed = 1 WHERE id = %s', ('REJECTED', company_id))
        db_conn.commit()

        # Get all company data from database
        cursor.execute('SELECT * FROM company')
        companies = cursor.fetchall()
    finally:
        cursor.close()

    return redirect(url_for('companyList', admin_id=admin_id))

# Admin add supervisor function
@app.route("/addSupervisor/<admin_id>/<supervisor_id>", methods=['GET', 'POST'])
def addSupervisorFunc(admin_id, supervisor_id):
    # Get user input name, email, phone number and password from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    password = request.args.get('password')

    print(supervisor_id)

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Insert supervisor data into database
        cursor.execute('INSERT INTO supervisor VALUES (%s, %s, %s, %s, %s)', (supervisor_id, password, name, email, phone))
        db_conn.commit()

        print('Supervisor added successfully')

        # Get all supervisor data from database
        cursor.execute('SELECT * FROM supervisor')
        supervisors = cursor.fetchall()
    finally:
        cursor.close()

    return redirect(url_for('supervisorList', admin_id=admin_id))

@app.route("/xy")
def xyPortfolio():
    return render_template('xy-portfolio.html')

@app.route("/kelvin")
def kelvinPortfolio():
    return render_template('kelvin-portfolio.html')

@app.route("/kh")
def khPortfolio():
    return render_template('kh-portfolio.html')

@app.route("/jt")
def jtPortfolio():
    return render_template('jt-portfolio.html')

@app.route("/yk")
def ykPortfolio():
    return render_template('yk-portfolio.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
