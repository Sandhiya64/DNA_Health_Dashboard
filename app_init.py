from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# Initialize Flask app
app = Flask(__name__)

# ✅ Ensure the database URI is set
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
print("Database URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))
# Initialize extensions
db = SQLAlchemy(app)  # ✅ Ensure db is initialized here
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
