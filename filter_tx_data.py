import pandas as pd
from datetime import datetime

df = pd.read_csv("data/2024_fut.csv", index_col=False, encoding="utf-8", low_memory=False)
print(df["契約"] == "TX")
df = df[df["契約"] == "TX"]
print(df)
