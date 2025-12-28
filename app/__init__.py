from flask import Flask
from flask_mysqldb import MySQL
import os

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'YOUR_KEY_HERE'  

    # --- DATABASE CONFIGURATION ---
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '' 
    app.config['MYSQL_DB'] = 'event_db'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    # --- UPLOAD FOLDER CONFIG ---
    base_dir = os.getcwd()
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'app/static/uploads')

    # Initialize Plugins
    mysql.init_app(app)

    # --- REGISTER BLUEPRINTS (CONTROLLERS) ---
    
    from app.controllers.main import main_bp
    from app.controllers.auth import auth_bp
    from app.controllers.admin import admin_bp
    from app.controllers.user import user_bp
    from app.controllers.api import api_bp  

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)

    return app
