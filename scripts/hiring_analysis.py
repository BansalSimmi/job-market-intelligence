import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED    = os.path.join(BASE_DIR, "data", "processed")
COMBINED_CSV = os.path.join(PROCESSED, "job_market_combined.csv")

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#F8F8F8",
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "font.family":      "sans-serif",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.labelsize":   11,
})

df = pd.read_csv(COMBINED_CSV)
df_f = df[df["source"] == "fresher_ds"].copy()
df_f["hired"] = pd.to_numeric(df_f["hired"], errors="coerce").fillna(0).astype(int)

total     = len(df_f)
hired     = df_f["hired"].sum()
hire_rate = 100 * hired / total
print(f"Total applications : {total}")
print(f"Hired              : {hired}  ({hire_rate:.1f}%)")


# 1. Hiring funnel
stage_order = ["Applied", "Shortlisted", "Interview", "Offered", "Hired", "Rejected"]
funnel = df_f["hiring_stage"].value_counts().reindex(stage_order).dropna()

fig, ax = plt.subplots(figsize=(10, 5))
bar_colors = ["#1D9E75" if s == "Hired" else "#E24B4A" if s == "Rejected" else "#9FE1CB" for s in funnel.index]
bars = ax.bar(funnel.index, funnel.values, color=bar_colors, width=0.6)
ax.set_title("Hiring funnel — where candidates drop off")
ax.set_ylabel("Applications")
for bar, val in zip(bars, funnel.values):
    pct = 100 * val / total
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"{val}\n({pct:.0f}%)", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(PROCESSED, "fig_hiring_funnel.png"), dpi=150, bbox_inches="tight")
plt.show()


# 2. Platform hire rate
platform_stats = (
    df_f.groupby("platform")
    .agg(total=("hired", "count"), hired=("hired", "sum"))
    .assign(hire_rate=lambda x: 100 * x["hired"] / x["total"])
    .query("total >= 20")
    .sort_values("hire_rate", ascending=False)
)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#0F6E56" if i == 0 else "#5DCAA5" for i in range(len(platform_stats))]
bars = ax.bar(platform_stats.index, platform_stats["hire_rate"], color=colors, width=0.6)
ax.set_title("Hire rate by platform (%)")
ax.set_ylabel("Hire rate (%)")
ax.set_ylim(0, platform_stats["hire_rate"].max() * 1.2)
for bar, (_, row) in zip(bars, platform_stats.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{row['hire_rate']:.1f}%\n(n={row['total']})", ha="center", va="bottom", fontsize=9)
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(PROCESSED, "fig_platform_hirerate.png"), dpi=150, bbox_inches="tight")
plt.show()


# 3. CGPA vs hire rate
df_f["cgpa_band"] = pd.cut(
    df_f["cgpa"],
    bins=[0, 6.5, 7.5, 8.5, 10],
    labels=["Below 6.5", "6.5–7.4", "7.5–8.4", "8.5+"]
)

cgpa_stats = (
    df_f.groupby("cgpa_band", observed=True)
    .agg(total=("hired", "count"), hired=("hired", "sum"))
    .assign(hire_rate=lambda x: 100 * x["hired"] / x["total"])
)

fig, ax1 = plt.subplots(figsize=(9, 5))
ax2 = ax1.twinx()
x = range(len(cgpa_stats))
ax1.bar(x, cgpa_stats["total"], color="#B5D4F4", label="Total applications", width=0.5)
ax2.plot(x, cgpa_stats["hire_rate"], color="#185FA5", marker="o", linewidth=2, label="Hire rate %")
ax1.set_xticks(x)
ax1.set_xticklabels(cgpa_stats.index)
ax1.set_ylabel("Applications", color="#185FA5")
ax2.set_ylabel("Hire rate (%)", color="#0F6E56")
ax1.set_title("CGPA band vs hire rate")
for xi, (_, row) in zip(x, cgpa_stats.iterrows()):
    ax2.text(xi, row["hire_rate"] + 0.5, f"{row['hire_rate']:.1f}%", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(PROCESSED, "fig_cgpa_hirerate.png"), dpi=150, bbox_inches="tight")
plt.show()


# 4. Feature correlation with hiring outcome
numeric_features = [
    "cgpa", "projects_count", "certifications_count",
    "linkedin_connections", "profile_completion_pct",
    "prior_internship", "referral_applied",
    "gap_year", "backlogs"
]
numeric_features = [f for f in numeric_features if f in df_f.columns]

correlations = (
    df_f[numeric_features + ["hired"]]
    .apply(pd.to_numeric, errors="coerce")
    .corr()["hired"]
    .drop("hired")
    .sort_values()
)

fig, ax = plt.subplots(figsize=(9, 6))
colors = ["#E24B4A" if v < 0 else "#1D9E75" for v in correlations.values]
bars = ax.barh(correlations.index, correlations.values, color=colors, height=0.6)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Correlation with being hired\n(+ve = increases hire chance)")
ax.set_xlabel("Pearson correlation with hired (0/1)")
for bar, val in zip(bars, correlations.values):
    ax.text(val + (0.003 if val >= 0 else -0.003), bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", ha="left" if val >= 0 else "right", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(PROCESSED, "fig_feature_correlation.png"), dpi=150, bbox_inches="tight")
plt.show()


# 5. Top skills among hired candidates
hired_skills = (
    df_f[df_f["hired"] == 1]["skills"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
    .str.lower()
    .value_counts()
    .head(15)
)

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(hired_skills.index[::-1], hired_skills.values[::-1], color="#534AB7", height=0.6)
ax.set_title("Top 15 skills among hired freshers")
ax.set_xlabel("Hired candidates with this skill")
for i, val in enumerate(hired_skills.values[::-1]):
    ax.text(val + 0.5, i, str(val), va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(PROCESSED, "fig_top_skills_hired.png"), dpi=150, bbox_inches="tight")
plt.show()


# 6. Summary
top_platform      = platform_stats.index[0]
top_platform_rate = platform_stats["hire_rate"].iloc[0]

print("\n" + "=" * 50)
print("Fresher Hiring — Key Numbers")
print("=" * 50)
print(f"Overall hire rate   : {hire_rate:.1f}%")
print(f"Best platform       : {top_platform} ({top_platform_rate:.1f}% hire rate)")
print(f"CGPA 8.5+ hire rate : {cgpa_stats.loc['8.5+', 'hire_rate']:.1f}%")
print(f"CGPA <6.5 hire rate : {cgpa_stats.loc['Below 6.5', 'hire_rate']:.1f}%")
print(f"Top positive factor : {correlations[correlations > 0].idxmax()}")
print(f"Top negative factor : {correlations.idxmin()}")
print(f"Top skill (hired)   : {hired_skills.index[0]}")
print("\nCharts saved to data/processed/")