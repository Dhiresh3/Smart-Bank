import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

df = pd.read_csv("C:/Users/dhire/OneDrive/Desktop/Coding1/laptop_price.csv", encoding="ISO-8859-1")

df['Price'] = round(df['Price_euros'] * 89.53).astype(int)

df['Ram'] = df['Ram'].str.replace('GB', '', regex=False).astype(int)

df['Touchscreen'] = df['ScreenResolution'].apply(lambda x: 1 if 'Touchscreen' in x else 0)
df['Ips'] = df['ScreenResolution'].apply(lambda x: 1 if 'IPS' in x.upper() else 0)

def extract_resolution(res_string, index):
    try:
        res_part = res_string.split()[0]
        return int(res_part.split('x')[index])
    except:
        return np.nan

df['X_res'] = df['ScreenResolution'].apply(lambda x: extract_resolution(x, 0))
df['Y_res'] = df['ScreenResolution'].apply(lambda x: extract_resolution(x, 1))

df.dropna(subset=['X_res', 'Y_res'], inplace=True)

df['PPI'] = ((df['X_res']**2 + df['Y_res']**2) ** 0.5) / df['Inches']

df['Weight'] = df['Weight'].str.replace('kg', '', regex=False).astype(float)
X = df[['Company', 'TypeName', 'Ram', 'Cpu', 'Gpu', 'OpSys', 'Weight', 'Touchscreen', 'Ips', 'PPI']]
y = np.log(df['Price'])

categorical = ['Company', 'TypeName', 'Cpu', 'Gpu', 'OpSys']

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
], remainder='passthrough')

pipe = Pipeline([
    ('preprocess', preprocessor),
    ('model', RandomForestRegressor(n_estimators=100, random_state=42))
])

pipe.fit(X, y)

pickle.dump(pipe, open('pipe.pkl', 'wb'))
print("✅ Model trained and saved as pipe.pkl")