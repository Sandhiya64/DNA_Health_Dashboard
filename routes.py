from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app_init import db, bcrypt, mail
from models import User, DNAReport
import joblib
import numpy as np
import pandas as pd
from flask_mail import Message
from app import app,db
# Load ML model
model = joblib.load('dna_model.pkl')

# Home route
@app.route('/')
def home():
    return "Welcome to the DNA-Based Personalized Health Dashboard!"

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Predict DNA route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_features = np.array(data["features"]).reshape(1, -1)
        prediction = model.predict(input_features)[0]
        return jsonify({"prediction": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)})

# Analyze DNA file
@app.route('/analyze_dna', methods=['POST'])
def analyze_dna():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    df = pd.read_csv(file)

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
    file = request.files['file']
    df = pd.read_csv(file)
    prediction = model.predict(df)

    new_report = DNAReport(user_id=current_user.id, file_name=file.filename, prediction=prediction[0])
    db.session.add(new_report)
    db.session.commit()

    send_email(current_user.email, "Your DNA Report is Ready", f"Your prediction: {prediction[0]}")

    return jsonify({"prediction": prediction.tolist()})

# User reports route
@app.route('/user_reports')
@login_required
def user_reports():
    reports = DNAReport.query.filter_by(user_id=current_user.id).all()
    return jsonify({"reports": [{"file_name": r.file_name, "prediction": r.prediction} for r in reports]})
