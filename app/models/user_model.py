from app import mysql
from datetime import datetime

class UserModel:
    @staticmethod
    def get_by_username(username):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cursor.fetchone()
        cursor.close()
        return user

    @staticmethod
    def create_user(username, password, email, role='user'):
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users(username, password, email, role, created_at) VALUES(%s, MD5(%s), %s, %s, NOW())", 
                       (username, password, email, role))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def update_last_login(username):
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET last_login = %s WHERE username=%s", (datetime.now(), username))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def get_full_profile(username):
        """Fetches User + Personal + Contact details joined together"""
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT u.username, u.role, u.profile_pic, p.*, c.*
            FROM users u
            LEFT JOIN has h ON u.uid = h.uid
            LEFT JOIN personal p ON h.pid = p.pid
            LEFT JOIN contact c ON p.pid = c.pid
            WHERE u.username = %s
        ''', [username])
        data = cursor.fetchone()
        cursor.close()
        return data

    @staticmethod
    def update_profile_pic(username, filename):
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET profile_pic = %s WHERE username = %s", (filename, username))
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def upsert_personal_info(username, fname, mname, lname, dob, gender, address, c1, c2, c3):
        """Updates personal info if exists, otherwise inserts new."""
        cursor = mysql.connection.cursor()
        
        # Check if personal info exists
        cursor.execute("SELECT * FROM has WHERE uid = (SELECT uid FROM users WHERE username = %s)", [username])
        exists = cursor.fetchone()

        if exists:
            cursor.execute('''UPDATE personal SET fname=%s, mname=%s, lname=%s, dob=%s, gender=%s, address=%s 
                              WHERE pid = (SELECT pid FROM has WHERE uid = (SELECT uid FROM users WHERE username=%s))''', 
                           (fname, mname, lname, dob, gender, address, username))
            cursor.execute('''UPDATE contact SET contact1=%s, contact2=%s, contact3=%s 
                              WHERE pid = (SELECT pid FROM has WHERE uid = (SELECT uid FROM users WHERE username=%s))''', 
                           (c1, c2, c3, username))
        else:
            cursor.execute("INSERT INTO personal(fname,mname,lname,dob,gender,address) VALUES(%s,%s,%s,%s,%s,%s)", 
                           (fname, mname, lname, dob, gender, address))
            pid = cursor.lastrowid
            cursor.execute("INSERT INTO contact VALUES(%s, %s, %s, %s)", (pid, c1, c2, c3))
            cursor.execute("INSERT INTO has VALUES((SELECT uid FROM users WHERE username=%s), %s)", (username, pid))
        
        mysql.connection.commit()
        cursor.close()
