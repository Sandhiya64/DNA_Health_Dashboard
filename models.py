from app_init import db, bcrypt
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        """Set the password hash for the user."""
        self.password = Bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the entered password matches the stored hash."""
        return bcrypt.check_password_hash(self.password, password)

    def get_id(self):
        """Return the user ID for Flask-Login."""
        return str(self.id)

# DNA Report model
class DNAReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    prediction = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', backref=db.backref('reports', lazy=True))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
