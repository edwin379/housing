"""Builds analysis.ipynb (run once; then just use the notebook)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

nb.cells = [
md("""# Are houses becoming less affordable?
**EDA homework — Edwin**

Question: compared to what people earn, are homes getting harder to buy?

**Data sources**
- OECD, *Analytical house price indicators* — price-to-income ratio (house price index ÷ disposable income per head, 2015 = 100), annual, 1990–2025: https://data-explorer.oecd.org/vis?df[ag]=OECD.ECO.MPD&df[id]=DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES
- 国土交通省 (MLIT), 不動産価格指数（住宅）, 2010 average = 100: https://www.mlit.go.jp/report/press/totikensangyo05_hh_000066.html
  - Nov 2020 values: https://www.mlit.go.jp/common/001388366.pdf
  - Dec 2025 values: https://japanpropertyresearch.com/ja/property-price-index
  - Sep 2025 Minami-Kanto values: https://www.haseko.co.jp/hri/cri/focus/focus-570/index.html

**How to read the ratio:** 100 = the 2015 relationship between house prices and income in that country. 130 means homes cost 30% more *relative to income* than in 2015. It compares a country with its own past — not countries with each other."""),

code("""import pandas as pd
import matplotlib.pyplot as plt
import requests, io

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e",
    "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.grid": True, "axes.axisbelow": True, "grid.color": "#ebeae4", "grid.linewidth": 0.8,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
})
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#b5b3ab", "#0b0b0b"
NAMES = {"JPN": "Japan", "KOR": "Korea", "CAN": "Canada", "USA": "United States",
         "AUS": "Australia", "NZL": "New Zealand", "GBR": "United Kingdom", "DEU": "Germany"}"""),

md("## 1. Load the OECD data\nTries the live OECD API first; if offline, uses the saved copy in `data/`."),

code("""URL = ("https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/"
       + "+".join(NAMES) + ".A.HPI_YDH.IX?startPeriod=1990&dimensionAtObservation=AllDimensions&format=csv")
try:
    r = requests.get(URL, timeout=30); r.raise_for_status()
    live = pd.read_csv(io.StringIO(r.text))
    df = (live.rename(columns={"REF_AREA": "country", "TIME_PERIOD": "year", "OBS_VALUE": "price_to_income_2015_100"})
              [["country", "year", "price_to_income_2015_100"]])
    df["year"] = df["year"].astype(int)
    df.to_csv("data/oecd_price_to_income.csv", index=False)
    print("Loaded LIVE from OECD")
except Exception as e:
    df = pd.read_csv("data/oecd_price_to_income.csv")
    print("Offline -> using saved CSV (", type(e).__name__, ")")

wide = df.pivot(index="year", columns="country", values="price_to_income_2015_100").rename(columns=NAMES)
wide.tail()"""),

code("""wide.describe().round(1)"""),

md("""## 2. First question: are homes less affordable than 10 years ago?
Compare 2025 with 2015 (=100)."""),

code("""chg = (wide.loc[2025] - 100).sort_values()
fig, ax = plt.subplots(figsize=(8, 4.2))
colors = [BLUE if c == "Japan" else (AQUA if v < 0 else GRAY) for c, v in chg.items()]
ax.barh(chg.index, chg.values, color=colors, height=0.6)
ax.axvline(0, color=INK, lw=1)
for i, v in enumerate(chg.values):
    ax.text(v + (1 if v >= 0 else -1), i, f"{v:+.0f}%", va="center",
            ha="left" if v >= 0 else "right", fontsize=10, color=INK)
ax.set_xlabel("Change in price-to-income ratio, 2015 → 2025")
ax.set_title("Mostly yes: in 7 of 8 countries homes cost more relative to income", loc="left", fontsize=13, color=INK)
ax.grid(axis="y", visible=False); ax.set_xlim(-35, 42)
plt.tight_layout(); plt.savefig("charts/fig1_change_since_2015.png", dpi=180); plt.show()"""),

md("""**First impression:** yes — Canada (+31%), the US (+26%), Australia (+20%) and Japan (+14%) all got less affordable. Korea is the only exception (−26%).

But 10 years is short. What happens if I look further back?"""),

md("## 3. Second question: what about the long run (1990–2025)?"),

code("""order = ["Japan", "Korea", "Germany", "United States", "Canada", "Australia", "New Zealand", "United Kingdom"]
fig, axes = plt.subplots(2, 4, figsize=(13, 6), sharex=True, sharey=True)
for ax, c in zip(axes.flat, order):
    for o in order:
        ax.plot(wide.index, wide[o], color="#e1dfd6", lw=1)
    col = BLUE if c in ("Japan", "Korea", "Germany") else ORANGE
    ax.plot(wide.index, wide[c], color=col, lw=2.2)
    ax.axhline(100, color="#8a887f", lw=0.8, ls="--")
    first, last = wide[c].iloc[0], wide[c].iloc[-1]
    ax.set_title(f"{c}\\n1990: {first:.0f} → 2025: {last:.0f}", loc="left", fontsize=10.5, color=INK)
fig.suptitle("Long view: Japan & Korea were LESS affordable in 1990; Canada, Australia, NZ, UK got much worse (2015 = 100)",
             x=0.01, ha="left", fontsize=14, color=INK)
fig.text(0.01, 0.005, "Blue = less affordable in 1990 than today · Orange = more affordable in 1990 than today. Source: OECD Analytical house price indicators",
         fontsize=9, color="#52514e")
plt.tight_layout(rect=(0, 0.03, 1, 0.95)); plt.savefig("charts/fig2_long_view.png", dpi=180); plt.show()"""),

code("""long = pd.DataFrame({"1990": wide.loc[1990], "2025": wide.loc[2025]})
long["change_%"] = ((long["2025"] / long["1990"] - 1) * 100).round(0)
long.sort_values("change_%").round(1)"""),

md("""**Surprise #1:** Japan was *far* less affordable in 1990 (182) than today (114) — the bubble economy. Korea fell from 345 to 74. Meanwhile Canada, Australia, New Zealand and the UK roughly doubled.

So "houses are getting less affordable" is true for the English-speaking countries, but Japan is **37% more affordable than in 1990**.

That sounded too good. Is it true for every kind of home in Japan?"""),

md("## 4. Third question: inside Japan, which homes?\nMLIT splits prices into residential land, detached houses and condos (マンション). Base: 2010 average = 100."),

code("""jp = pd.read_csv("data/mlit_japan_price_index.csv")
jp"""),

code("""nat = jp[jp["region"] == "Japan (national)"].set_index("period")
tokyo = jp[jp["region"].str.startswith("Minami")].iloc[0]
types = [("residential_land", "Land"), ("detached_house", "Detached house"), ("condo", "Condo (mansion)")]

fig, ax = plt.subplots(figsize=(9, 4.6))
x = range(len(types)); w = 0.26
for k, (per, shade) in enumerate([("2010 avg", "#e1dfd6"), ("2020-11", "#b5b3ab"), ("2025-12", None)]):
    vals = [nat.loc[per, t] for t, _ in types]
    cols = [shade] * 3 if shade else ["#6f6d66", "#6f6d66", ORANGE]
    bars = ax.bar([i + (k - 1) * w for i in x], vals, w * 0.92, color=cols)
    bars[0].set_label(per)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.0f}", ha="center", fontsize=9, color=INK)
ax.scatter([2 + 1.55 * w], [tokyo["condo"]], s=60, color=ORANGE, edgecolor="white", zorder=5)
ax.annotate(f"Tokyo area (Minami-Kanto)\\nSep 2025: {tokyo['condo']:.0f}", (2 + 1.55 * w, tokyo["condo"]),
            xytext=(10, -8), textcoords="offset points", fontsize=9, color=INK)
ax.set_xticks(list(x)); ax.set_xticklabels([n for _, n in types])
ax.set_ylabel("Price index (2010 = 100)"); ax.set_ylim(0, 245)
ax.legend(title="Period", frameon=False, loc="upper left")
ax.set_title("Japan's condos more than doubled since 2010 — land and houses rose ~20%", loc="left", fontsize=13, color=INK)
ax.grid(axis="x", visible=False)
fig.text(0.01, 0.005, "Source: MLIT Real Estate Price Index (Residential). 2020 = seasonally adjusted, 2025 = original series.", fontsize=9, color="#52514e")
plt.tight_layout(rect=(0, 0.03, 1, 1)); plt.savefig("charts/fig3_japan_types.png", dpi=180); plt.show()"""),

code("""ratio = nat.loc["2025-12", "condo"] / nat.loc["2025-12", "detached_house"]
print(f"Since 2010, condo prices grew {nat.loc['2025-12','condo']-100:.0f}% vs detached houses {nat.loc['2025-12','detached_house']-100:.0f}%")
print(f"Condo index is {ratio:.1f}x the detached-house index")"""),

md("""**Surprise #2:** Japan's national average hides a split. Condos are up **121%** since 2010, detached houses only **20%**. Condos are the homes young city workers buy (near stations, in Tokyo/Osaka), so for them affordability *did* get much worse.

## 5. What I learned
1. **First chart:** "Yes, homes are less affordable" — 7 of 8 countries got worse since 2015.
2. **Longer view changed it:** Japan and Korea are *more* affordable than in 1990. The "affordability crisis" is mainly Canada, Australia, NZ, the UK and the US.
3. **Zooming into Japan changed it again:** the average is calm, but condos doubled. Affordability depends on *what* and *where* you buy.

**Limits:** the OECD ratio is an index (each country vs its own 2015), so it can't say Japan is cheaper than Canada in absolute terms. MLIT values are a few published snapshots, not a full series; income growth in Japan since 2010 was small, so the condo price rise is mostly a real affordability loss."""),

md("""## 6. Export data for the scrolling web page (`index.html`)"""),

code("""import json
story = {
    "years": wide.index.tolist(),
    "countries": {c: [round(v, 1) for v in wide[c].tolist()] for c in order},
    "japan_types": {p: {t: float(nat.loc[p, t]) for t, _ in types} for p in nat.index},
    "tokyo_condo_2025_09": float(tokyo["condo"]),
}
json.dump(story, open("data/story_data.json", "w"), ensure_ascii=False, indent=1)
print("saved data/story_data.json")"""),
]

nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "analysis.ipynb")
print("analysis.ipynb written")
