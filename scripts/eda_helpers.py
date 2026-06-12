# EDA Part 1: Salary trends, city analysis, role demand

# Job Market Intelligence — EDA Part 1: Market Overview
# Goal: Surface salary trends, top cities, and in-demand roles

# %% — Imports & setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#F8F8F8",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "sans-serif",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.labelsize":   11,
})

# %% — Load data
df = pd.read_csv(r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\processed\job_market_combined.csv")
df_salary  = df[df["source"] == "salary_ds"].copy()
df_fresher = df[df["source"] == "fresher_ds"].copy()

print(f"Salary DS: {len(df_salary)} rows")
print(f"Fresher DS: {len(df_fresher)} rows")
print(f"\nSalary range: INR {df_salary['salary_inr'].min():,.0f} - INR {df_salary['salary_inr'].max():,.0f}")
print(f"Unique cities: {df_salary['city'].nunique()}")
print(f"Unique roles:  {df_salary['job_role'].nunique()}")


# 1. Salary distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Salary Distribution — Indian Job Market", fontsize=14, fontweight="bold", y=1.02)

# Histogram
sal = df_salary["salary_inr"].dropna()
axes[0].hist(sal, bins=40, color="#1D9E75", edgecolor="white", linewidth=0.5)
axes[0].set_title("Distribution of monthly salary (₹)")
axes[0].set_xlabel("Monthly salary (₹)")
axes[0].set_ylabel("Number of listings")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
median_sal = sal.median()
axes[0].axvline(median_sal, color="#993C1D", linestyle="--", linewidth=1.5, label=f"Median ₹{median_sal:,.0f}")
axes[0].legend(fontsize=10)

# Box plot by top 8 cities
top_cities = df_salary["city"].value_counts().head(8).index
df_top = df_salary[df_salary["city"].isin(top_cities)]
city_order = df_top.groupby("city")["salary_inr"].median().sort_values(ascending=False).index
data_by_city = [df_top[df_top["city"] == c]["salary_inr"].dropna().values for c in city_order]
bp = axes[1].boxplot(data_by_city, labels=city_order, patch_artist=True, vert=True,
                      medianprops=dict(color="#993C1D", linewidth=2))
for patch in bp["boxes"]:
    patch.set_facecolor("#9FE1CB")
    patch.set_alpha(0.7)
axes[1].set_title("Salary spread — top 8 cities")
axes[1].set_xlabel("City")
axes[1].set_ylabel("Monthly salary (₹)")
axes[1].tick_params(axis="x", rotation=45)
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))

plt.tight_layout()
plt.savefig(r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\processed\fig_salary_distribution.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: fig_salary_distribution.png")

# 2. Top 10 cities by average salary
city_salary = (
    df_salary.groupby("city")["salary_inr"]
    .agg(avg_salary="mean", count="count")
    .query("count >= 10")
    .sort_values("avg_salary", ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#0F6E56" if i < 3 else "#5DCAA5" for i in range(len(city_salary))]
bars = ax.barh(city_salary.index[::-1], city_salary["avg_salary"][::-1], color=colors[::-1], height=0.6)
ax.set_title("Top 10 cities by average monthly salary", fontsize=13, fontweight="bold")
ax.set_xlabel("Average monthly salary (₹)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1000:.0f}K"))
for bar, (city, row) in zip(bars[::-1], city_salary.iterrows()):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
            f"₹{row['avg_salary']/1000:.1f}K  (n={row['count']})",
            va="center", fontsize=9, color="#3d3d3a")
ax.set_xlim(0, city_salary["avg_salary"].max() * 1.25)
plt.tight_layout()
plt.savefig(r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\processed\fig_top_cities_salary.png", dpi=150, bbox_inches="tight")
plt.show()


# 3. Top 15 most in-demand job roles
role_demand = df_salary["job_role"].value_counts().head(15)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(role_demand.index[::-1], role_demand.values[::-1], color="#534AB7", height=0.6)
ax.set_title("Top 15 most listed job roles", fontsize=13, fontweight="bold")
ax.set_xlabel("Number of listings")
for i, (role, count) in enumerate(zip(role_demand.index[::-1], role_demand.values[::-1])):
    ax.text(count + 0.5, i, str(count), va="center", fontsize=9)
plt.tight_layout()
plt.savefig(r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\processed\fig_role_demand.png", dpi=150, bbox_inches="tight")
plt.show()

# 4. Salary heatmap — top roles × top cities
top_roles  = df_salary["job_role"].value_counts().head(8).index
top_cities_h = df_salary["city"].value_counts().head(8).index

pivot = (
    df_salary[df_salary["job_role"].isin(top_roles) & df_salary["city"].isin(top_cities_h)]
    .groupby(["job_role", "city"])["salary_inr"]
    .mean()
    .unstack(fill_value=np.nan)
)

fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(pivot.values / 1000, cmap="YlGn", aspect="auto")
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=9)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, fontsize=9)
ax.set_title("Average salary heatmap (₹K) — roles × cities", fontsize=13, fontweight="bold")
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Avg salary (₹ thousands)")
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        if not np.isnan(val):
            ax.text(j, i, f"{val/1000:.0f}K", ha="center", va="center", fontsize=8,
                    color="black" if val/1000 < 40 else "white")
plt.tight_layout()
plt.savefig(r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\processed\fig_salary_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

# 5. Key insights summary
print("=" * 55)
print("KEY INSIGHTS - Market Overview")
print("=" * 55)
print(f"\n1. Median monthly salary: INR {df_salary['salary_inr'].median():,.0f}")
print(f"   Mean monthly salary:   INR {df_salary['salary_inr'].mean():,.0f}")
print(f"\n2. Top-paying city:  {city_salary.index[0]} (INR {city_salary['avg_salary'].iloc[0]:,.0f}/mo)")
print(f"   2nd highest city: {city_salary.index[1]} (INR {city_salary['avg_salary'].iloc[1]:,.0f}/mo)")
print(f"\n3. Most listed role: {role_demand.index[0]} ({role_demand.iloc[0]} listings)")
print(f"\n4. Cities covered:   {df_salary['city'].nunique()}")
print(f"   Roles covered:   {df_salary['job_role'].nunique()}")
print("\nAll charts saved to data/processed/")
print("\nNext: Run 02_hiring_analysis.ipynb for fresher hiring insights")