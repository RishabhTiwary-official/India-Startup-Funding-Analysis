import pandas as pd
from sqlalchemy import create_engine

# ── Load database ──────────────────────────────────────
engine = create_engine("sqlite:///startup_funding.db")

print("=" * 55)
print("   INDIA STARTUP FUNDING — DEEP ANALYSIS")
print("=" * 55)

# ══════════════════════════════════════════════════════
# ANALYSIS 1 — Top 15 Most Active Investors
# ══════════════════════════════════════════════════════
query1 = """
SELECT Investors,
       COUNT(*) as Total_Deals,
       SUM(Amount_USD) as Total_Invested
FROM funding
WHERE Investors != 'Undisclosed Investors'
GROUP BY Investors
ORDER BY Total_Deals DESC
LIMIT 15
"""
print("\n📊 ANALYSIS 1 — Top 15 Most Active Investors:")
print(pd.read_sql(query1, engine).to_string())

# ══════════════════════════════════════════════════════
# ANALYSIS 2 — Investment Type Breakdown
# Seed vs Series A vs Series B etc.
# ══════════════════════════════════════════════════════
query2 = """
SELECT Investment_Type,
       COUNT(*) as Total_Deals,
       SUM(Amount_USD) as Total_Funding,
       AVG(Amount_USD) as Avg_Deal_Size
FROM funding
GROUP BY Investment_Type
ORDER BY Total_Deals DESC
"""
print("\n📊 ANALYSIS 2 — Investment Type Breakdown:")
print(pd.read_sql(query2, engine).to_string())

# ══════════════════════════════════════════════════════
# ANALYSIS 3 — Quick Commerce Deep Dive
# Zepto, Blinkit, Swiggy, BigBasket, Dunzo
# ══════════════════════════════════════════════════════
query3 = """
SELECT Startup_Name, Date, Industry,
       Investment_Type, Amount_USD, Investors
FROM funding
WHERE Startup_Name LIKE '%Blinkit%'
   OR Startup_Name LIKE '%Zepto%'
   OR Startup_Name LIKE '%Swiggy%'
   OR Startup_Name LIKE '%BigBasket%'
   OR Startup_Name LIKE '%Dunzo%'
   OR Startup_Name LIKE '%Grofers%'
ORDER BY Amount_USD DESC
"""
print("\n📊 ANALYSIS 3 — Quick Commerce Startups Funding:")
print(pd.read_sql(query3, engine).to_string())

# ══════════════════════════════════════════════════════
# ANALYSIS 4 — Sector Growth Year by Year
# Which sector grew fastest?
# ══════════════════════════════════════════════════════
query4 = """
SELECT Year, Industry,
       COUNT(*) as Deals,
       SUM(Amount_USD) as Total_Funding
FROM funding
WHERE Year IS NOT NULL
  AND Industry IS NOT NULL
GROUP BY Year, Industry
ORDER BY Year, Total_Funding DESC
"""
df_growth = pd.read_sql(query4, engine)

print("\n📊 ANALYSIS 4 — Top Industry Each Year:")
for year in sorted(df_growth["Year"].dropna().unique()):
    top = df_growth[df_growth["Year"] == year].iloc[0]
    print(f"  {int(year)} → {top['Industry']} "
          f"(${top['Total_Funding']:,.0f} | {int(top['Deals'])} deals)")

# ══════════════════════════════════════════════════════
# ANALYSIS 5 — City Performance Deep Dive
# ══════════════════════════════════════════════════════
query5 = """
SELECT City,
       COUNT(*) as Total_Deals,
       SUM(Amount_USD) as Total_Funding,
       AVG(Amount_USD) as Avg_Deal_Size
FROM funding
WHERE City IS NOT NULL
GROUP BY City
ORDER BY Total_Funding DESC
LIMIT 8
"""
print("\n📊 ANALYSIS 5 — Top 8 Cities Deep Dive:")
print(pd.read_sql(query5, engine).to_string())

# ── Save clean data for Tableau ────────────────────────
df_clean = pd.read_sql("SELECT * FROM funding", engine)
df_clean.to_csv("startup_clean.csv", index=False)
print("\n✅ Clean CSV saved — startup_clean.csv (ready for Tableau!)")

# ══════════════════════════════════════════════════════
# FIX — Merge Bangalore + Bengaluru
# ══════════════════════════════════════════════════════
print("\n📊 ANALYSIS 6 — City Fix (Bangalore + Bengaluru merged):")
df_city = pd.read_sql("SELECT * FROM funding", engine)
df_city["City"] = df_city["City"].str.strip()
df_city["City"] = df_city["City"].replace({
    "Bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "New delhi": "New Delhi",
    "new delhi": "New Delhi",
    "gurugram": "Gurgaon",
    "Gurugram": "Gurgaon"
})
city_fixed = df_city.groupby("City").agg(
    Total_Deals=("Amount_USD", "count"),
    Total_Funding=("Amount_USD", "sum")
).sort_values("Total_Funding", ascending=False).head(8)
print(city_fixed)

# ══════════════════════════════════════════════════════
# ANALYSIS 7 — Quick Commerce Funding Timeline
# How did funding grow year by year?
# ══════════════════════════════════════════════════════
print("\n📊 ANALYSIS 7 — Quick Commerce Funding by Year:")
qc_companies = ["Swiggy", "BigBasket", "Grofers", "Dunzo"]
df_all = pd.read_sql("SELECT * FROM funding", engine)
df_qc = df_all[df_all["Startup_Name"].isin(qc_companies)]
qc_yearly = df_qc.groupby(["Year", "Startup_Name"])["Amount_USD"].sum().reset_index()
qc_yearly = qc_yearly[qc_yearly["Amount_USD"] > 0]
print(qc_yearly.to_string())

# ══════════════════════════════════════════════════════
# ANALYSIS 8 — Average Deal Size by Investment Stage
# ══════════════════════════════════════════════════════
print("\n📊 ANALYSIS 8 — Clean Investment Stages:")
df_stage = pd.read_sql("SELECT * FROM funding", engine)
df_stage["Stage"] = df_stage["Investment_Type"].str.strip()
df_stage["Stage"] = df_stage["Stage"].replace({
    "Seed/ Angel Funding": "Seed",
    "Seed / Angel Funding": "Seed",
    "Seed/Angel Funding": "Seed",
    "Seed\\nFunding": "Seed",
    "Seed Funding": "Seed",
    "Seed funding": "Seed",
    "Seed Round": "Seed",
    "Pre-Series A": "Pre-Series A",
    "pre-Series A": "Pre-Series A",
    "pre-series A": "Pre-Series A",
    "Private Equity": "Private Equity",
    "Private\\nEquity": "Private Equity",
    "PrivateEquity": "Private Equity"
})
stage_summary = df_stage.groupby("Stage").agg(
    Deals=("Amount_USD", "count"),
    Avg_Size=("Amount_USD", "mean"),
    Total=("Amount_USD", "sum")
).sort_values("Total", ascending=False).head(10)
print(stage_summary)