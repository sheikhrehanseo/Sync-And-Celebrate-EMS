from flask import Blueprint, render_template, session
from app import mysql

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def index():
    try:
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
    except Exception as e:
        public_events = []
        print(f"Database Error: {e}")

    if 'loggedin' in session:
        return render_template('index.html', session=session['loggedin'], name=session['username'], public_events=public_events)
    else:
        return render_template('index.html', session=False, public_events=public_events)

@main_bp.route('/events')
def public_events_list():
    cursor = mysql.connection.cursor()
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

    is_loggedin = session.get('loggedin', False)
    username = session.get('username', None)

    return render_template('public_events.html', session=is_loggedin, name=username, events=events)
