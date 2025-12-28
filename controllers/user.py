from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from app import mysql
from app.models.user_model import UserModel
from app.models.event_model import EventModel
import os
from datetime import datetime

user_bp = Blueprint('user', __name__)

# Pricing Data (Moved here from app.py to keep Controller logic self-contained)
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

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/users/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'loggedin' in session and username == session['username']:
        # Use Model to get data
        pdata = UserModel.get_full_profile(username)
        event_details = EventModel.get_user_events(username)
        
        # Simple count query
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(eid) as count FROM books WHERE uid = (SELECT uid FROM users WHERE username = %s)", [session['username']])
        count_event = cursor.fetchone()
        cursor.close()

        return render_template('dashboard.html', name=username, pdata=pdata, cn=count_event, events=event_details)
    return render_template('login.html')

@user_bp.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'loggedin' in session:
        if request.method == "POST":
            # File Upload Logic
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{session['username']}_{int(datetime.now().timestamp())}_{filename}"
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    UserModel.update_profile_pic(session['username'], filename)

            # Update Personal Info via Model
            UserModel.upsert_personal_info(
                session['username'], 
                request.form['fname'], request.form['mname'], request.form['lname'],
                request.form['dob'], request.form['gender'].capitalize(), request.form['address'],
                request.form['contact1'], request.form['contact2'], request.form['contact3']
            )
            return redirect(url_for('user.dashboard', username=session['username']))

        # GET Request
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT p.* ,c.* FROM personal p NATURAL JOIN contact c WHERE pid = (SELECT pid from has where uid = (SELECT uid from users where username=%s))", [session['username']])
        details = cursor.fetchone()
        cursor.close()
        return render_template('personal.html', session=session['loggedin'], name=session['username'], details=details)
    return redirect(url_for('auth.login'))

@user_bp.route('/<eventname>', methods=['GET', 'POST'])
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

        # Logic
        venue = ev['venue']
        tier = ev['tier']
        max_people = int(ev['max'])
        date = ev['edate']
        requests = ev['requests']
        visibility = ev.get('visibility', 'private')
        meal_pref = ev.get('meal_pref', 'Standard')
        final_requests = f"{requests} | Meal Preference: {meal_pref}"

        selected_extras = request.form.getlist('extras')
        extras_string = ", ".join(selected_extras)
        extra_cost = 0
        if 'DJ' in selected_extras: extra_cost += 5000
        if 'SoundSystem' in selected_extras: extra_cost += 3000
        if 'ValetParking' in selected_extras: extra_cost += 2000

        # Check availability
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM event WHERE edate = %s", (date,))
        existing_event = cursor.fetchone()
        cursor.close()

        if existing_event:
            return render_template('booking.html', session=session.get('loggedin'), name=session.get('username'), event=eventname.capitalize(), error_message=f"Date {date} is taken.")

        # Calc Cost
        tier_key = tier if tier.startswith('tier') else f'tier{tier}'
        base_cost = pricing[eventname][tier_key]['base']
        per_person = pricing[eventname][tier_key]['person']
        total_cost = base_cost + (max_people * per_person) + extra_cost

        # Create Event via Model
        eid = EventModel.create_event(etype, date, tier, total_cost, venue, max_people, final_requests, visibility, extras_string)
        EventModel.book_event(session['username'], eid, person1, person2)
        
        return redirect(url_for('user.dashboard', username=session['username']))

    # GET Request
    if eventname in events_available:
        if 'loggedin' in session:
            # Check if profile exists
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT pid FROM has WHERE uid = (SELECT uid from users where username = %s)", [session['username']])
            per_details = cursor.fetchone()
            cursor.close()
            
            if not per_details:
                return redirect(url_for('user.personal'))
                
            return render_template('booking.html', session=session['loggedin'], name=session['username'], event=eventname.capitalize(), t1_base=pricing[eventname]['tier1']['base'], t2_base=pricing[eventname]['tier2']['base'], t3_base=pricing[eventname]['tier3']['base'], t4_base=pricing[eventname]['tier4']['base'], t1_per=pricing[eventname]['tier1']['person'], t2_per=pricing[eventname]['tier2']['person'], t3_per=pricing[eventname]['tier3']['person'], t4_per=pricing[eventname]['tier4']['person'])
        else:
            return redirect(url_for('auth.login'))
    return redirect(url_for('main.index'))

@user_bp.route('/ticket/<int:event_id>')
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
    return redirect(url_for('auth.login'))
