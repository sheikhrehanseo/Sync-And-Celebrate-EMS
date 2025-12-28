from flask import Blueprint, render_template, request, redirect, url_for, session
from app import mysql
from datetime import datetime

# Define the Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = MD5(%s)", (username, password))
        account = cursor.fetchone()
        cursor.close()

        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = account['role']
            
            # Update last login
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET last_login = %s WHERE username=%s", (datetime.now(), session['username']))
            mysql.connection.commit()
            cursor.close()

            if account['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard')) # Note: 'admin.' prefix
            return redirect(url_for('main.index')) # Note: 'main.' prefix
        else:
            return render_template("login.html", msg="Invalid Username or Password!")
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    rmsg = ""
    if request.method == "POST":
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']
        email = userDetails['email']
        repass = userDetails['reenterPassword']
        if password != repass:
            return render_template("register.html", rmsg="Password does not match!")
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", [username])
            account = cursor.fetchone()
            if account:
                cursor.close()
                return render_template("register.html", rmsg="Username already exists!")
            else:
                cursor.execute("INSERT INTO users(username,password,email,role,created_at) VALUES(%s,MD5(%s),%s,'user',NOW())", (username, password, email))
                mysql.connection.commit()
                cursor.close()
            return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
