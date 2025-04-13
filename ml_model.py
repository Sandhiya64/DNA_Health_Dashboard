from pyexpat import model
import pandas as pd
import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

df = pd.read_csv('your_data.csv')
X = df.drop(columns=['target_column'])
y = df['target_column']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter tuning using GridSearchCV
param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]}
grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid_search.fit(X_train, y_train)

# Get the best model and save it
best_model = grid_search.best_estimator_
joblib.dump(best_model, 'dna_model.pkl')

# Evaluate the model accuracy
y_pred = best_model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
