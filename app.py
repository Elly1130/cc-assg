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

# Route to admin home page
@app.route("/admin/<admin_id>")
def admin(admin_id):
    return render_template('admin.html', admin_id=admin_id)

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

# Route to supervisor list page
@app.route("/admin/supervisorList", methods=['GET'])
def supervisorList():
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get all supervisor data from database
        cursor.execute('SELECT * FROM supervisor')
        supervisors = cursor.fetchall()
    finally:
        cursor.close()

    return render_template('supervisorList.html', supervisors=supervisors)

# Admin edit profile function
@app.route("/editProfile/<admin_id>")
def editProfile(admin_id):
    print(admin_id);

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
            return redirect(url_for('admin', admin_id=admin_id))
        else:
            # If password incorrect, redirect to admin login page with error message
            msg = 'Account exists but password incorrect'
            return render_template('adminLogin.html', msg=msg)
    # If account not exists in accounts table in out database
    else:
        msg = 'Account does not exists'
        return render_template('adminLogin.html', msg=msg)
    

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
