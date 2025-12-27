from flask import Flask, render_template, request, redirect, session, url_for, Response, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
import csv
import io
from flask import Response

app = Flask(__name__)
app.secret_key = 'YOUR_KEY_Here'

# --- CONFIGURATION ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'event_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Image Upload Config
UPLOAD_FOLDER = '/home/sheikhrehan/mysite/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- PRICING DATA ---
pricing = {
    'birthday': {
        'tier1': {'base': 7500, 'person': 750},
        'tier2': {'base': 10000, 'person': 1000},
        'tier3': {'base': 12500, 'person': 1250},
        'tier4': {'base': 17000, 'person': 1550},
    },
    'anniversary': {
        'tier1': {'base': 9000, 'person': 1000},
        'tier2': {'base': 12000, 'person': 1300},
        'tier3': {'base': 15000, 'person': 1600},
        'tier4': {'base': 20000, 'person': 1900},
    },
    'other': {
        'tier1': {'base': 8000, 'person': 875},
        'tier2': {'base': 11000, 'person': 1150},
        'tier3': {'base': 14000, 'person': 1400},
        'tier4': {'base': 18500, 'person': 1700},
    },
}
events_available = ['birthday', 'anniversary', 'other']

# --- ROUTES ---

@app.route('/')
@app.route('/home')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT e.*, u.username
        FROM event e
        JOIN books b ON e.eid = b.eid
        JOIN users u ON b.uid = u.uid
        WHERE e.visibility = 'public' AND e.edate >= CURDATE()
        ORDER BY e.edate ASC
        LIMIT 6
    """)
    public_events = cursor.fetchall()
    cursor.close()

    if 'loggedin' in session:
        return render_template('index.html', session=session['loggedin'], name=session['username'], public_events=public_events)
    else:
        return render_template('index.html', session=False, public_events=public_events)

@app.route('/users/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'loggedin' in session and username == session['username']:
        cursor = mysql.connection.cursor()

        # Fetch Personal Details (includes profile_pic now if you updated DB)
        cursor.execute(
            '''
            SELECT u.username, u.role, u.profile_pic, p.*, c.*
            FROM users u
            LEFT JOIN has h ON u.uid = h.uid
            LEFT JOIN personal p ON h.pid = p.pid
            LEFT JOIN contact c ON p.pid = c.pid
            WHERE u.username = %s
            ''',
            [session['username']],
        )
        pdata = cursor.fetchone()

        cursor.execute("SELECT COUNT(eid) as count FROM books WHERE uid = (SELECT uid FROM users WHERE username = %s)", [session['username']])
        count_event = cursor.fetchone()

        cursor.execute(
            '''
            SELECT e.*, b.*
            FROM event e NATURAL JOIN books b
            WHERE e.eid IN (SELECT eid FROM books WHERE uid = (SELECT uid FROM users WHERE username = %s))
            ''',
            [session['username']],
        )
        event_details = cursor.fetchall()

        return render_template('dashboard.html', name=username, pdata=pdata, cn=count_event, events=event_details)
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = MD5(%s)", (username, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = account['role']
            cursor.execute("UPDATE users SET last_login = %s WHERE username=%s", (datetime.now(), session['username']))
            mysql.connection.commit()
            cursor.close()

            if account['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return render_template('index.html', session=session['loggedin'], name=session['username'], msg="Login Successful!")
        else:
            return render_template("login.html", msg="Invalid Username or Password!")
    return render_template('login.html')

# --- NEW: CSV EXPORT FOR ADMIN ---
@app.route('/admin/download_report')
@admin_login_required
def download_report():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT e.eid, e.etype, e.edate, e.evenue, e.ecost, e.status, u.username, u.email
        FROM event e
        JOIN books b ON e.eid = b.eid
        JOIN users u ON b.uid = u.uid
        ORDER BY e.edate DESC
    """)
    result = cursor.fetchall()
    cursor.close()

    output = io.StringIO()
    writer = csv.writer(output)
    # Headers
    writer.writerow(['Event ID', 'Type', 'Date', 'Venue', 'Cost (PKR)', 'Status', 'Client Username', 'Client Email'])
    # Data
    for row in result:
        writer.writerow([row['eid'], row['etype'], row['edate'], row['evenue'], row['ecost'], row['status'], row['username'], row['email']])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=booking_report.csv"}
    )

# --- NEW: DEDICATED PUBLIC EVENTS PAGE ---
@app.route('/events')
def public_events_list():
    cursor = mysql.connection.cursor()
    # Fetch ALL upcoming public events (Index only shows 6, this shows all)
    cursor.execute("""
        SELECT e.*, u.username
        FROM event e
        JOIN books b ON e.eid = b.eid
        JOIN users u ON b.uid = u.uid
        WHERE e.visibility = 'public' AND e.edate >= CURDATE()
        ORDER BY e.edate ASC
    """)
    events = cursor.fetchall()
    cursor.close()

    # Check login status for the navbar
    is_loggedin = session.get('loggedin', False)
    username = session.get('username', None)

    return render_template('public_events.html', session=is_loggedin, name=username, events=events)


@app.route('/register', methods=['GET', 'POST'])
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
                return render_template("register.html", rmsg="Username already exists!")
            else:
                cursor.execute("INSERT INTO users(username,password,email,role,created_at) VALUES(%s,MD5(%s),%s,'user',NOW())", (username, password, email))
                mysql.connection.commit()
                cursor.close()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/<eventname>', methods=['GET', 'POST'])
def book_event(eventname: str):
    if request.method == 'POST':
        ev = request.form
        person1 = person2 = None
        if eventname == 'birthday':
            person1 = ev['person1']
            etype = 'Birthday'
        elif eventname == 'anniversary':
            person1 = ev['person1']
            person2 = ev['person2']
            etype = 'Anniversary'
        else:
            etype = ev['etype']

        venue = ev['venue']
        tier = ev['tier']
        max_people = int(ev['max'])
        date = ev['edate']
        requests = ev['requests']
        visibility = ev.get('visibility', 'private')
        meal_pref = ev.get('meal_pref', 'Standard')
        final_requests = f"{requests} | Meal Preference: {meal_pref}"

        # Extras Logic
        selected_extras = request.form.getlist('extras')
        extras_string = ", ".join(selected_extras)
        extra_cost = 0
        if 'DJ' in selected_extras: extra_cost += 5000
        if 'SoundSystem' in selected_extras: extra_cost += 3000
        if 'ValetParking' in selected_extras: extra_cost += 2000

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM event WHERE edate = %s", (date,))
        existing_event = cursor.fetchone()

        if existing_event:
            return render_template('booking.html', session=session.get('loggedin'), name=session.get('username'), event=eventname.capitalize(), error_message=f"Date {date} is taken.")

        # Cost Calculation
        tier_key = tier if tier.startswith('tier') else f'tier{tier}'
        base_cost = pricing[eventname][tier_key]['base']
        per_person = pricing[eventname][tier_key]['person']
        total_cost = base_cost + (max_people * per_person) + extra_cost

        cursor.execute('''INSERT INTO event(etype, edate, etier, ecost, evenue, emax_people, especial, status, visibility, extras) VALUES(%s,%s,%s,%s,%s,%s,%s,'pending', %s, %s)''', (etype, date, tier, total_cost, venue, max_people, final_requests, visibility, extras_string))
        cursor.execute('''INSERT INTO books VALUES((SELECT uid FROM users WHERE username=%s), (SELECT LAST_INSERT_ID()), %s,%s)''', (session['username'], person1, person2))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard', username=session['username']))

    if eventname in events_available:
        if 'loggedin' in session:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT pid FROM has WHERE uid = (SELECT uid from users where username = %s)", [session['username']])
            per_details = cursor.fetchone()
            if not per_details:
                return redirect(url_for('personal'))
            return render_template('booking.html', session=session['loggedin'], name=session['username'], event=eventname.capitalize(), t1_base=pricing[eventname]['tier1']['base'], t2_base=pricing[eventname]['tier2']['base'], t3_base=pricing[eventname]['tier3']['base'], t4_base=pricing[eventname]['tier4']['base'], t1_per=pricing[eventname]['tier1']['person'], t2_per=pricing[eventname]['tier2']['person'], t3_per=pricing[eventname]['tier3']['person'], t4_per=pricing[eventname]['tier4']['person'])
        else:
            return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()

        if request.method == "POST":
            firstname = request.form['fname']
            middlename = request.form['mname']
            lastname = request.form['lname']
            DOB = request.form['dob']
            contact1 = request.form['contact1']
            contact2 = request.form['contact2']
            contact3 = request.form['contact3']
            gender = request.form['gender']
            address = request.form['address']

            # --- FILE UPLOAD LOGIC ---
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Unique filename
                    filename = f"{session['username']}_{int(datetime.now().timestamp())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Update DB
                    cursor.execute("UPDATE users SET profile_pic = %s WHERE username = %s", (filename, session['username']))
                    mysql.connection.commit()

            # --- DETAILS LOGIC ---
            cursor.execute("SELECT * FROM has WHERE uid = (SELECT uid FROM users WHERE username = %s)", [session['username']])
            personal_exists = cursor.fetchone()

            if personal_exists:
                cursor.execute('''UPDATE personal SET fname=%s, mname=%s, lname=%s, dob=%s, gender=%s, address=%s WHERE pid = (SELECT pid FROM has WHERE uid = (SELECT uid FROM users WHERE username=%s))''', (firstname, middlename, lastname, DOB, gender.capitalize(), address, session['username']))
                cursor.execute('''UPDATE contact SET contact1=%s, contact2=%s, contact3=%s WHERE pid = (SELECT pid FROM has WHERE uid = (SELECT uid FROM users WHERE username=%s))''', (contact1, contact2, contact3, session['username']))
            else:
                cursor.execute("INSERT INTO personal(fname,mname,lname,dob,gender,address) VALUES(%s,%s,%s,%s,%s,%s)", (firstname, middlename, lastname, DOB, gender.capitalize(), address))
                cursor.execute("INSERT INTO contact VALUES((SELECT LAST_INSERT_ID()), %s, %s, %s)", (contact1, contact2, contact3))
                cursor.execute("INSERT INTO has VALUES((SELECT uid FROM users WHERE username=%s), (SELECT LAST_INSERT_ID()))", [session['username']])

            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('dashboard', username=session['username']))

        # GET request
        cursor.execute("SELECT p.* ,c.* FROM personal p NATURAL JOIN contact c WHERE pid = (SELECT pid from has where uid = (SELECT uid from users where username=%s))", [session['username']])
        details = cursor.fetchone()
        cursor.close()
        return render_template('personal.html', session=session['loggedin'], name=session['username'], details=details)
    return redirect(url_for('login'))

@app.route('/ticket/<int:event_id>')
def ticket(event_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT e.*, u.username, u.email, p.fname, p.lname, p.address, c.contact1
            FROM event e
            JOIN books b ON e.eid = b.eid
            JOIN users u ON b.uid = u.uid
            LEFT JOIN has h ON u.uid = h.uid
            LEFT JOIN personal p ON h.pid = p.pid
            LEFT JOIN contact c ON p.pid = c.pid
            WHERE e.eid = %s
        """, [event_id])
        data = cursor.fetchone()
        cursor.close()
        if data:
            return render_template('ticket.html', data=data)
        return "Ticket not found", 404
    return redirect(url_for('login'))

# --- ADMIN (CRUD) ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = MD5(%s) AND role = 'admin'", (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        return render_template("admin_login.html", msg="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    cursor = mysql.connection.cursor()
    curr_date = datetime.now().strftime('%Y-%m-%d')
    # Update statuses
    cursor.execute("UPDATE event SET status = CASE WHEN edate < %s THEN 'completed' WHEN edate >= %s AND status != 'canceled' THEN 'pending' ELSE status END", (curr_date, curr_date))
    mysql.connection.commit()

    # --- Basic Stats ---
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()['total_users']
    cursor.execute("SELECT COUNT(*) as total_events FROM event")
    total_events = cursor.fetchone()['total_events']
    cursor.execute("SELECT SUM(ecost) as total_revenue FROM event")
    total_revenue = cursor.fetchone()['total_revenue'] or 0
    cursor.execute("SELECT AVG(ecost) as avg_event_cost FROM event")
    avg_event_cost = cursor.fetchone()['avg_event_cost'] or 0

    # --- Growth Stats ---
    cursor.execute("SELECT COUNT(*) as users_last_7_days FROM users WHERE DATE(last_login) >= CURDATE() - INTERVAL 7 DAY")
    users_last_7_days = cursor.fetchone()['users_last_7_days']
    cursor.execute("SELECT COUNT(*) as events_last_month FROM event WHERE edate >= CURDATE() - INTERVAL 1 MONTH")
    events_last_month = cursor.fetchone()['events_last_month']

    cursor.execute("SELECT COUNT(*) as total_users_last_week FROM users WHERE DATE(last_login) >= CURDATE() - INTERVAL 7 DAY")
    total_users_last_week = cursor.fetchone()['total_users_last_week'] or 1
    user_growth = round((users_last_7_days - total_users_last_week) / total_users_last_week * 100, 2)

    cursor.execute("SELECT COUNT(*) as total_events_last_week FROM event WHERE edate >= CURDATE() - INTERVAL 7 DAY")
    total_events_last_week = cursor.fetchone()['total_events_last_week'] or 1
    event_growth = round((events_last_month - total_events_last_week) / total_events_last_week * 100, 2)

    cursor.execute("SELECT SUM(ecost) as total_revenue_last_week FROM event WHERE edate >= CURDATE() - INTERVAL 7 DAY")
    total_revenue_last_week = cursor.fetchone()['total_revenue_last_week'] or 1
    revenue_growth = round((total_revenue - total_revenue_last_week) / total_revenue_last_week * 100, 2)

    # --- Lists & Tables ---
    cursor.execute("SELECT etype, COUNT(*) as count FROM event GROUP BY etype ORDER BY count DESC LIMIT 5")
    top_events = cursor.fetchall()
    cursor.execute("SELECT * FROM users ORDER BY last_login DESC LIMIT 5")
    recent_users = cursor.fetchall()
    cursor.execute("SELECT e.*, u.username, e.status FROM event e JOIN books b ON e.eid = b.eid JOIN users u ON b.uid = u.uid ORDER BY e.edate DESC LIMIT 10")
    recent_events = cursor.fetchall()
    cursor.execute("SELECT u.*, COUNT(b.eid) as event_count FROM users u LEFT JOIN books b ON u.uid = b.uid GROUP BY u.uid")
    users = cursor.fetchall()

    # --- Chart Data (Restored Logic) ---
    cursor.execute("SELECT DATE(edate) as date, COUNT(*) as count FROM event WHERE edate >= CURDATE() - INTERVAL 30 DAY GROUP BY DATE(edate) ORDER BY date")
    bookings_data = cursor.fetchall()
    bookings_labels = [str(row['date']) for row in bookings_data]
    bookings_data_values = [row['count'] for row in bookings_data]

    cursor.execute("SELECT etype, SUM(ecost) as revenue FROM event GROUP BY etype ORDER BY revenue DESC")
    revenue_data = cursor.fetchall()
    revenue_labels = [row['etype'] for row in revenue_data]
    revenue_data_values = [row['revenue'] for row in revenue_data]

    cursor.execute("SELECT DATE(created_at) as date, COUNT(*) as count FROM users WHERE created_at >= CURDATE() - INTERVAL 30 DAY GROUP BY DATE(created_at) ORDER BY date")
    user_reg_data = cursor.fetchall()
    user_reg_labels = [str(row['date']) for row in user_reg_data]
    user_reg_data_values = [row['count'] for row in user_reg_data]

    cursor.execute("SELECT status, COUNT(*) as count FROM event GROUP BY status")
    event_status_data = cursor.fetchall()
    event_status_labels = [row['status'] for row in event_status_data]
    event_status_data_values = [row['count'] for row in event_status_data]

    # --- Extra Stats ---
    cursor.execute("SELECT COUNT(*) as completed_events FROM event WHERE status = 'completed'")
    completed_events = cursor.fetchone()['completed_events']
    cursor.execute("SELECT COUNT(*) as pending_events FROM event WHERE status = 'pending'")
    pending_events = cursor.fetchone()['pending_events']
    cursor.execute("""
        SELECT AVG(TIMESTAMPDIFF(HOUR, u.created_at, e.edate)) as avg_booking_time
        FROM event e
        JOIN books b ON e.eid = b.eid
        JOIN users u ON b.uid = u.uid
        WHERE e.edate >= u.created_at
    """)
    avg_booking_time = cursor.fetchone()['avg_booking_time'] or 0

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_events=total_events,
        total_revenue=total_revenue,
        avg_event_cost=avg_event_cost,
        users_last_7_days=users_last_7_days,
        events_last_month=events_last_month,
        user_growth=user_growth,
        event_growth=event_growth,
        revenue_growth=revenue_growth,
        top_events=top_events,
        recent_users=recent_users,
        users=users,
        bookings_labels=bookings_labels,
        bookings_data=bookings_data_values,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data_values,
        user_reg_labels=user_reg_labels,
        user_reg_data=user_reg_data_values,
        event_status_labels=event_status_labels,
        event_status_data=event_status_data_values,
        completed_events=completed_events,
        pending_events=pending_events,
        avg_booking_time=avg_booking_time,
        recent_events=recent_events
    )
# CRUD Routes
@app.route('/admin/delete_user', methods=['POST'])
@admin_login_required
def delete_user():
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE uid = %s", [request.form['user_id']])
    mysql.connection.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == "POST":
        u = request.form
        if u['password'] != u['reenterPassword']: return render_template("admin_register.html", rmsg="Mismatch")
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users(username,password,email,role,created_at) VALUES(%s,MD5(%s),%s,'admin',NOW())", (u['username'], u['password'], u['email']))
        mysql.connection.commit()
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html')

@app.route('/admin/delete_event', methods=['POST'])
@admin_login_required
def delete_event():
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM books WHERE eid = %s", [request.form['event_id']])
    cursor.execute("DELETE FROM event WHERE eid = %s", [request.form['event_id']])
    mysql.connection.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_event/<int:event_id>', methods=['GET'])
@admin_login_required
def edit_event_form(event_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM event WHERE eid = %s", [event_id])
    event = cursor.fetchone()
    return render_template('edit_event.html', event=event) if event else redirect(url_for('admin_dashboard'))

@app.route('/admin/update_event', methods=['POST'])
@admin_login_required
def update_event():
    f = request.form
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE event SET edate=%s, evenue=%s, emax_people=%s, status=%s WHERE eid=%s', (f['edate'], f['evenue'], f['emax_people'], f['status'], f['event_id']))
    mysql.connection.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/cancel_event', methods=['POST'])
@admin_login_required
def cancel_event():
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE event SET status = 'canceled' WHERE eid = %s", [request.form['event_id']])
    mysql.connection.commit()
    return redirect(url_for('admin_dashboard'))

# ==========================================
#  REST API ENDPOINTS (Assignment Requirement)
# ==========================================

# 1. READ ALL Resources (GET) - Already implemented, but here is the dedicated API version
@app.route('/api/events/all', methods=['GET'])
def api_get_all_events():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM event")
    events = cursor.fetchall()
    cursor.close()
    return jsonify(events), 200

# 2. CREATE Resource (POST) [cite: 21]
@app.route('/api/event/create', methods=['POST'])
def api_create_event():
    # Check if request is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Extract data from JSON
    etype = data.get('etype')
    edate = data.get('edate')
    evenue = data.get('evenue')
    ecost = data.get('ecost')
    visibility = data.get('visibility', 'private')
    
    # Insert into Database
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO event (etype, edate, evenue, ecost, visibility) VALUES (%s, %s, %s, %s, %s)",
        (etype, edate, evenue, ecost, visibility)
    )
    mysql.connection.commit()
    new_id = cursor.lastrowid
    cursor.close()
    
    return jsonify({"message": "Event created successfully", "id": new_id}), 201

# 3. UPDATE Resource (PUT) [cite: 27]
@app.route('/api/event/update/<int:id>', methods=['PUT'])
def api_update_event(id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    new_venue = data.get('evenue')
    
    cursor = mysql.connection.cursor()
    # Check if event exists first
    cursor.execute("SELECT * FROM event WHERE eid = %s", (id,))
    event = cursor.fetchone()
    
    if not event:
        cursor.close()
        return jsonify({"error": "Event not found"}), 404
        
    # Update the venue (Example update)
    cursor.execute("UPDATE event SET evenue = %s WHERE eid = %s", (new_venue, id))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({"message": "Event updated successfully", "eid": id}), 200

# 4. DELETE Resource (DELETE) 
@app.route('/api/event/delete/<int:id>', methods=['DELETE'])
def api_delete_event(id):
    cursor = mysql.connection.cursor()
    
    # Check if exists
    cursor.execute("SELECT * FROM event WHERE eid = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Event not found"}), 404
        
    # Delete the event
    cursor.execute("DELETE FROM event WHERE eid = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({"message": "Event deleted successfully", "eid": id}), 200

if __name__ == '__main__':
    app.run(debug=True)
