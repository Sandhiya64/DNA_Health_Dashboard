from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from app_init import app, db
from models import User, DNAReport
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length




bcrypt = Bcrypt(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your email password
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
print("Database URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))

# Initialize extensions
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load ML model
model = joblib.load('dna_model.pkl')
print("ML Model Loaded Successfully!")
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database and create tables
with app.app_context():
    db.create_all()
class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Register')
# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Home route
@app.route('/')
def home():
    return "Welcome to the DNA-Based Personalized Health Dashboard!"

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)  # This will set the session using Flask-Login
            flash("Login successful!", "success")
            next_page = request.args.get('next') 
            print(f"User {email} logged in successfully!")  # Debug print
            return redirect(request.args.get('next') or url_for('dashboard'))
        else:
            flash("Invalid username or password", "danger")
            print(f"Failed login attempt for {email}")  # Debug print

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log the user out
    return redirect(url_for('login'))  # Redirect to login page

# Predict DNA route
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)
        
        # Optional: Validate input structure here
        if df.empty:
            return jsonify({'error': 'Uploaded CSV is empty'}), 400

        input_features = df.values
        predictions = model.predict(input_features)

        # Convert predictions to list for JSON response
        return jsonify({'predictions': predictions.tolist()})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analyze DNA file route
@app.route('/analyze_dna', methods=['POST'])
def analyze_dna():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    # Read and print raw content
    content = file.read().decode("utf-8")
    print("File Content:\n", content)  # Debugging step

    # Move file pointer back to the beginning
    file.stream.seek(0)

    try:
        df = pd.read_csv(file)
        print(df.head())  # Debugging step
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Return the actual error message

    prediction = "High risk" if df['GeneX'].mean() > 0.5 else "Low risk"
    return jsonify({"prediction": prediction})

# Send email function
def send_email(to, subject, body):
    msg = Message(subject, sender="your_email@gmail.com", recipients=[to])
    msg.body = body
    mail.send(msg)

# Predict DNA for authenticated users
@app.route('/predict_dna', methods=['POST'])
@login_required
def predict_dna():
    try:
        if 'file' not in request.files:
            print("No file part in request.files")  # Debug
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        print("Received file:", file.filename)  # Debug

        if not file.filename.endswith('.csv'):
            print("File is not a CSV")  # Debug
            return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

        df = pd.read_csv(file)
        print("CSV DataFrame:\n", df.head())  # Debug

        encoder = LabelEncoder()
        df['Gene'] = encoder.fit_transform(df['Gene'])
        df['Allele 1'] = encoder.fit_transform(df['Allele 1'])
        df['Allele 2'] = encoder.fit_transform(df['Allele 2'])

        X = df[['GeneX', 'GeneY', 'GeneZ']]
        prediction = model.predict(X)

        print("Prediction successful:", prediction.tolist())  # Debug
        return jsonify({"prediction": prediction.tolist()})

    except Exception as e:
        print("🔥 Error in predict_dna route:", str(e))
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
@app.route('/chart_data')
@login_required
def chart_data():
    reports = DNAReport.query.filter_by(user_id=current_user.id).all()
    data = [{"date": report.timestamp.strftime("%Y-%m-%d"), "result": report.result} for report in reports]
    return jsonify(data)
# User reports route
@app.route('/user_reports')
@login_required  # This ensures the user is logged in
def user_reports():
    # Fetch reports only if the user is authenticated
    reports = DNAReport.query.filter_by(user_id=current_user.id).all()
    return render_template('user_reports.html', reports=reports)

if __name__ == "__main__":
    app.run(debug=True)
print("Model type:", type(model))
