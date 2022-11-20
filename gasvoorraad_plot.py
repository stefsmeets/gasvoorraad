import requests
import altair as alt
import pandas as pd

from secrets import TOKEN

url = "https://agsi.gie.eu/api"

params = {
    "country": "nl",
    "from": "2022-01-01",
    #     "to": "2022-10-21",
    "size": 300,
}

header = {
    "x-key": TOKEN,
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

base = (
    alt.Chart(df)
    .mark_line()
    .encode(x=alt.X("gasDayStart:T", axis=alt.Axis(title="Datum")))
)

line = base.mark_line(color="red").encode(
    y=alt.Y(
        "full:Q",
        axis=alt.Axis(title="Vulniveau (%)"),
        scale=alt.Scale(padding=0, domain=[0, 100]),
    )
)

bar = base.mark_bar().encode(
    y=alt.Y("injection", axis=alt.Axis(title="Gastoevoer (GWh/d)"))
)

chart = bar + line

today = datetime.date.today()

chart = chart.properties(title=f"Gasvoorraad in Nederland\nUpdated {today}").resolve_scale(
    y="independent"
)

chart.save(
    "chart.json", 
    json_kwds={
        'indent': 0,
    })

# breakpoint()
