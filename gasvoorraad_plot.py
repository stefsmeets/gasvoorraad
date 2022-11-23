import altair as alt
from datetime import date
import pandas as pd
import requests
import sys

try:
    TOKEN = sys.argv[1]
except IndexError:
    from secrets import TOKEN

url = "https://agsi.gie.eu/api"

header = {
    "x-key": TOKEN,
}

for year in sys.argv[1:]:
    print(f'Processing {year}')

    params = {
        "country": "nl",
        "from": f"{year}-01-01",
        "to": f"{year}-12-31",
        "size": 365,
    }

    r = requests.get(url=url, params=params, headers=header)
    data = r.json()

    df = pd.json_normalize(data["data"])

    df["gasDayStart"] = pd.to_datetime(df["gasDayStart"])

    for col in (
        "gasInStorage",
        "consumption",
        "consumptionFull",
        "injection",
        "withdrawal",
        "netWithdrawal",
        "workingGasVolume",
        "injectionCapacity",
        "withdrawalCapacity",
        "trend",
        "full",
    ):
        df[col] = df[col].astype(float)


    df['withdrawal'] = -df['withdrawal']

    # per_day = df.melt(id_vars=('gasDayStart',), value_vars=('injection', 'withdrawal'))
    per_week = (df.groupby([pd.Grouper(key = 'gasDayStart', freq = 'W')])
    .agg(injectie = ('injection' , 'sum'), afname = ('withdrawal', 'sum'))
    .round()).melt(ignore_index=False).reset_index()

    line = alt.Chart(df).mark_line(color='red').encode(
        x=alt.X("gasDayStart:T", axis=alt.Axis(title="Datum")),
        y=alt.Y('full:Q', 
           axis=alt.Axis(title="Vulniveau (%)"),
           scale=alt.Scale(padding=0, domain=[0, 100])),
        tooltip=['gasDayStart', 'full']
    )

    bar = alt.Chart(
        per_week
    ).mark_bar(
        binSpacing=0, opacity=0.6
    # ).mark_area(
    #      interpolate='step-after', opacity=0.6, line=False,
    ).encode(
        x=alt.X("gasDayStart:T", 
                axis=alt.Axis(title="Datum"),
                scale=alt.Scale(domain=[f"{year}-01-01", f"{year}-12-31"]),
            ),
        y=alt.Y("value:Q", 
                axis=alt.Axis(title="Gastoevoer (GWh/week)"), 
                scale=alt.Scale(padding=0, domain=[-15000, 15000]),
                stack=None,
            ),
        color='variable',
        tooltip=['gasDayStart', 'variable', 'value'],
    )

    chart = line + bar

    today = date.today()

    chart = chart.properties(title=f"Gasvoorraad in Nederland {year}").resolve_scale(
        y="independent"
    ).interactive()

    chart.save(
        f"chart-{year}.json", 
        json_kwds={
            'indent': 0,
        })
    chart.save(f"chart-{year}.html")

# breakpoint()
