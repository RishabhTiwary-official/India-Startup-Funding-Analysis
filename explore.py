import pandas as pd

# Load the dataset
df = pd.read_csv("startup_funding.csv", encoding="latin1")

# Basic info
print("Shape of dataset:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nBasic statistics:")
print(df.describe())