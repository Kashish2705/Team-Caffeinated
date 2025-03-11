import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import pickle
import joblib
import os

def prediction(f):    # Load dataset
    df = pd.read_csv(f)  # Change to actual file path
    new_df = df.copy()
    df = df.iloc[1:]

    # Drop unnecessary columns
    columns_to_drop = ["Unique ID", "Start Date", "End Date",'Q18_1 What specific product that you are currently using would the shown product replace?\n Please type in ONE specific brand or product per space provided.',
        'Q18_2 What specific product that you are currently using would the shown concept replace?\n Please type in ONE specific brand or product per space provided.',
        'Q18_3 What specific product that you are currently using would the shown concept replace?\n Please type in ONE specific brand or product per space provided.']
    df = df.drop(columns=columns_to_drop, errors="ignore")

    # # Drop rows where target is missing
    # df = df.dropna(subset=["OE_Quality_Flag"])
    df.head()
    # Identify categorical columns automatically
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    # Apply Label Encoding to all categorical features
    encoder = LabelEncoder()
    for col in categorical_columns:
        df[col] = encoder.fit_transform(df[col].astype(str))

    # X = df.drop('OE_Quality_Flag',axis='columns')

    model = joblib.load(open('model.pkl','rb'))

    # Ensure the model is valid
    if not hasattr(model, "predict"):
        raise TypeError("Loaded object is not a trained model. Check your pickle file!")

    y_pred = model.predict(df)  # Predict using the model

    # Add predictions to DataFrame
    new_df['Predictions'] = 0
    if len(y_pred) == len(new_df) - 1:
        new_df.loc[1:, 'Predictions'] = y_pred  # Start from index 1
    else:
        print("Error: y_pred length does not match expected range")

    return new_df

#prediction()
#prediction('test_data.csv')