from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import RegisterForm, LoginForm
from flask import jsonify
import joblib
import numpy as np
import pandas as pd
app = Flask(__name__)
model = joblib.load("ml_model.pkl")
print("ML Model Loaded Successfully!")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
@app.route('/')
def home():
    return "Welcome to the DNA-Based Personalized Health Dashboard!"
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id  # Store user in session
            flash('Login successful!', 'success')
            print("Login successful")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({'id': user.id, 'name': user.name, 'email': user.email})
    return jsonify({'error': 'User not found'}), 404
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract features from JSON
        input_features = np.array(data["features"]).reshape(1, -1)  # Convert to 2D array

        # Make a prediction
        prediction = model.predict(input_features)[0]

        # Return the prediction as JSON
        return jsonify({"prediction": float(prediction)})

    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/analyze_dna', methods=['POST'])
def analyze_dna():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    # Read and print raw content
    content = file.read().decode("utf-8")
    print("File Content:\n", content)  # Debugging step

    # Move file pointer back to the beginning
    file.seek(0)

    try:
        df = pd.read_csv(file)
        print(df.head())  # Debugging step
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Return the actual error message

    prediction = "High risk" if df['GeneX'].mean() > 0.5 else "Low risk"
    return jsonify({"prediction": prediction})
model = joblib.load('dna_model.pkl')

@app.route('/predict_dna', methods=['POST'])
def predict_dna():
    file = request.files['file']
    df = pd.read_csv(file)

    prediction = model.predict(df)
    return jsonify({"prediction": prediction.tolist()})
@app.route('/chart_data', methods=['GET'])
def chart_data():
    return jsonify({"data": [0.8, 0.3, 0.6]})

if __name__ == "__main__":
    app.run(debug=True)
