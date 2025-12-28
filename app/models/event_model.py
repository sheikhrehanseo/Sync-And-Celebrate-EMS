from app import mysql

class EventModel:
    @staticmethod
    def get_all_public():
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
        return events

    @staticmethod
    def get_by_id(eid):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM event WHERE eid = %s", [eid])
        event = cursor.fetchone()
        cursor.close()
        return event
    
    @staticmethod
    def create_event(etype, edate, etier, ecost, evenue, emax, especial, visibility, extras):
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO event(etype, edate, etier, ecost, evenue, emax_people, especial, status, visibility, extras) 
                          VALUES(%s,%s,%s,%s,%s,%s,%s,'pending', %s, %s)''', 
                       (etype, edate, etier, ecost, evenue, emax, especial, visibility, extras))
        mysql.connection.commit()
        eid = cursor.lastrowid
        cursor.close()
        return eid

    @staticmethod
    def book_event(username, eid, person1, person2):
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO books VALUES((SELECT uid FROM users WHERE username=%s), %s, %s, %s)''', 
                       (username, eid, person1, person2))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def get_user_events(username):
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT e.*, b.*
            FROM event e NATURAL JOIN books b
            WHERE e.eid IN (SELECT eid FROM books WHERE uid = (SELECT uid FROM users WHERE username = %s))
        ''', [username])
        events = cursor.fetchall()
        cursor.close()
        return events

    @staticmethod
    def delete_event(eid):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM books WHERE eid = %s", [eid])
        cursor.execute("DELETE FROM event WHERE eid = %s", [eid])
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def update_event(eid, edate, evenue, emax, status):
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE event SET edate=%s, evenue=%s, emax_people=%s, status=%s WHERE eid=%s', 
                       (edate, evenue, emax, status, eid))
        mysql.connection.commit()
        cursor.close()
