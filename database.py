import pandas as pd
from sqlalchemy import create_engine

# ── Load raw data ──────────────────────────────────────
df = pd.read_csv("startup_funding.csv", encoding="latin1")

# ── Step 1: Clean column names ─────────────────────────
df.columns = [
    "Sr_No", "Date", "Startup_Name", "Industry",
    "Sub_Industry", "City", "Investors",
    "Investment_Type", "Amount_USD", "Remarks"
]
print("✅ Column names cleaned!")
print(df.columns.tolist())

# ── Step 2: Drop useless column ────────────────────────
df = df.drop(columns=["Remarks", "Sr_No"])
print("\n✅ Remarks and Sr_No columns dropped!")

# ── Step 3: Clean Amount column ────────────────────────
df["Amount_USD"] = df["Amount_USD"].astype(str)
df["Amount_USD"] = df["Amount_USD"].str.replace(",", "")
df["Amount_USD"] = df["Amount_USD"].str.replace("undisclosed", "0", case=False)
df["Amount_USD"] = pd.to_numeric(df["Amount_USD"], errors="coerce")
df["Amount_USD"] = df["Amount_USD"].fillna(0)
print("\n✅ Amount column cleaned!")

# ── Step 4: Clean Date column ──────────────────────────
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
print("\n✅ Date column cleaned — Year and Month extracted!")

# ── Step 5: Create SQLite Database ─────────────────────
engine = create_engine("sqlite:///startup_funding.db")
df.to_sql("funding", engine, if_exists="replace", index=False)
print("\n✅ SQL Database created — startup_funding.db!")

# ── Step 6: Test SQL Query ─────────────────────────────
query = "SELECT Startup_Name, Industry, Amount_USD FROM funding ORDER BY Amount_USD DESC LIMIT 10"
top10 = pd.read_sql(query, engine)
print("\n📊 Top 10 Startups by Funding Amount:")
print(top10.to_string())

# ── More SQL Queries ───────────────────────────────────

# Top 5 Industries by total funding
query2 = """
SELECT Industry, 
       COUNT(*) as Total_Deals,
       SUM(Amount_USD) as Total_Funding
FROM funding 
GROUP BY Industry 
ORDER BY Total_Funding DESC 
LIMIT 5
"""
print("\n📊 Top 5 Industries by Total Funding:")
print(pd.read_sql(query2, engine).to_string())

# Top 5 Cities for startup funding
query3 = """
SELECT City,
       COUNT(*) as Total_Deals,
       SUM(Amount_USD) as Total_Funding
FROM funding
GROUP BY City
ORDER BY Total_Deals DESC
LIMIT 5
"""
print("\n📊 Top 5 Cities by Number of Deals:")
print(pd.read_sql(query3, engine).to_string())

# Funding by Year
query4 = """
SELECT Year,
       COUNT(*) as Total_Deals,
       SUM(Amount_USD) as Total_Funding
FROM funding
WHERE Year IS NOT NULL
GROUP BY Year
ORDER BY Year
"""
print("\n📊 Funding Trend by Year:")
print(pd.read_sql(query4, engine).to_string())