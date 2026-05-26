import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# ── Setup ──────────────────────────────────────────────
engine = create_engine("sqlite:///startup_funding.db")
sns.set_theme(style="darkgrid")
plt.rcParams["figure.figsize"] = (12, 6)

# ── Load & Fix Data ────────────────────────────────────
df = pd.read_sql("SELECT * FROM funding", engine)
df["City"] = df["City"].str.strip().replace({
    "Bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "Gurugram": "Gurgaon",
    "New delhi": "New Delhi"
})

# ══════════════════════════════════════════════════════
# CHART 1 — Top 8 Cities by Total Funding
# ══════════════════════════════════════════════════════
city_data = df.groupby("City")["Amount_USD"].sum().sort_values(
    ascending=False).head(8).reset_index()
city_data["Amount_Billion"] = city_data["Amount_USD"] / 1e9

plt.figure()
bars = sns.barplot(data=city_data, x="City", y="Amount_Billion",
                   hue="City", palette="viridis", legend=False)
plt.title("Top 8 Indian Cities by Total Startup Funding",
          fontsize=14, fontweight="bold")
plt.xlabel("City")
plt.ylabel("Total Funding ($ Billion)")
for bar, val in zip(bars.patches, city_data["Amount_Billion"]):
    bars.text(bar.get_x() + bar.get_width()/2,
              bar.get_height() + 0.1,
              f"${val:.1f}B", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("chart1_cities.png", dpi=150)
plt.close()
print("✅ Chart 1 saved — Top Cities")

# ══════════════════════════════════════════════════════
# CHART 2 — Quick Commerce Funding Growth (Line Chart)
# ══════════════════════════════════════════════════════
qc = df[df["Startup_Name"].isin(["Swiggy", "BigBasket", "Grofers", "Dunzo"])]
qc_yearly = qc.groupby(["Year", "Startup_Name"])["Amount_USD"].sum().reset_index()
qc_yearly = qc_yearly[qc_yearly["Amount_USD"] > 0]
qc_yearly["Amount_M"] = qc_yearly["Amount_USD"] / 1e6

plt.figure()
for company in ["Swiggy", "BigBasket", "Grofers", "Dunzo"]:
    data = qc_yearly[qc_yearly["Startup_Name"] == company]
    if not data.empty:
        plt.plot(data["Year"], data["Amount_M"],
                 marker="o", linewidth=2.5, label=company, markersize=8)

plt.title("Quick Commerce Startups — Funding Growth 2015–2019",
          fontsize=14, fontweight="bold")
plt.xlabel("Year")
plt.ylabel("Total Funding ($ Million)")
plt.legend()
plt.tight_layout()
plt.savefig("chart2_qc_growth.png", dpi=150)
plt.close()
print("✅ Chart 2 saved — Quick Commerce Growth")

# ══════════════════════════════════════════════════════
# CHART 3 — Top 10 Investors by Deal Count
# ══════════════════════════════════════════════════════
investors = df[~df["Investors"].str.lower().str.contains(
    "undisclosed", na=True)]
top_inv = investors.groupby("Investors")["Amount_USD"].count(
).sort_values(ascending=False).head(10).reset_index()
top_inv.columns = ["Investor", "Deals"]

plt.figure()
sns.barplot(data=top_inv, x="Deals", y="Investor",
            hue="Investor", palette="coolwarm", legend=False)
plt.title("Top 10 Most Active Investors in Indian Startups",
          fontsize=14, fontweight="bold")
plt.xlabel("Number of Deals")
plt.ylabel("Investor")
plt.tight_layout()
plt.savefig("chart3_investors.png", dpi=150)
plt.close()
print("✅ Chart 3 saved — Top Investors")

# ══════════════════════════════════════════════════════
# CHART 4 — Funding Trend by Year
# ══════════════════════════════════════════════════════
yearly = df.groupby("Year")["Amount_USD"].sum().reset_index()
yearly = yearly.dropna()
yearly["Amount_B"] = yearly["Amount_USD"] / 1e9

plt.figure()
plt.bar(yearly["Year"], yearly["Amount_B"],
        color=sns.color_palette("magma", len(yearly)))
plt.plot(yearly["Year"], yearly["Amount_B"],
         color="white", marker="o", linewidth=2)
plt.title("Indian Startup Funding by Year — 2015 to 2020",
          fontsize=14, fontweight="bold")
plt.xlabel("Year")
plt.ylabel("Total Funding ($ Billion)")
for i, row in yearly.iterrows():
    plt.text(row["Year"], row["Amount_B"] + 0.1,
             f"${row['Amount_B']:.1f}B", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("chart4_yearly_trend.png", dpi=150)
plt.close()
print("✅ Chart 4 saved — Yearly Trend")

# ══════════════════════════════════════════════════════
# CHART 5 — Quick Commerce Total Funding Comparison
# ══════════════════════════════════════════════════════
qc_total = qc.groupby("Startup_Name")["Amount_USD"].sum().reset_index()
qc_total["Amount_M"] = qc_total["Amount_USD"] / 1e6
qc_total = qc_total.sort_values("Amount_M", ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(data=qc_total, x="Startup_Name", y="Amount_M",
            hue="Startup_Name", palette="Set2", legend=False)
plt.title("Quick Commerce — Total Funding Raised (2015–2019)",
          fontsize=14, fontweight="bold")
plt.xlabel("Company")
plt.ylabel("Total Funding ($ Million)")
for bar, val in zip(plt.gca().patches, qc_total["Amount_M"]):
    plt.gca().text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + 2,
                   f"${val:.0f}M", ha="center", fontsize=10)
plt.tight_layout()
plt.savefig("chart5_qc_comparison.png", dpi=150)
plt.close()
print("✅ Chart 5 saved — QC Comparison")

# ══════════════════════════════════════════════════════
# CHART 6 — Investment Stage Breakdown
# ══════════════════════════════════════════════════════
stage_map = {
    "Seed Funding": "Seed", "Seed/ Angel Funding": "Seed",
    "Seed / Angel Funding": "Seed", "Seed\\nFunding": "Seed",
    "Seed/Angel Funding": "Seed", "Seed Round": "Seed",
    "Seed funding": "Seed", "Private\\nEquity": "Private Equity",
    "PrivateEquity": "Private Equity", "pre-Series A": "Pre-Series A",
    "pre-series A": "Pre-Series A", "Pre-series A": "Pre-Series A"
}
df["Clean_Stage"] = df["Investment_Type"].str.strip().replace(stage_map)
stage_data = df.groupby("Clean_Stage")["Amount_USD"].sum(
).sort_values(ascending=False).head(8).reset_index()
stage_data["Amount_B"] = stage_data["Amount_USD"] / 1e9

plt.figure()
sns.barplot(data=stage_data, x="Amount_B", y="Clean_Stage",
            hue="Clean_Stage", palette="Blues_d", legend=False)
plt.title("Total Funding by Investment Stage",
          fontsize=14, fontweight="bold")
plt.xlabel("Total Funding ($ Billion)")
plt.ylabel("Investment Stage")
plt.tight_layout()
plt.savefig("chart6_stages.png", dpi=150)
plt.close()
print("✅ Chart 6 saved — Investment Stages")

print("\n🎉 All 6 charts saved successfully!")