import pandas as pd
from datetime import datetime

df = pd.read_csv("data/2024_fut.csv", index_col=False, encoding="utf-8", low_memory=False)

# Filter for TX contracts only
df = df[df["契約"] == "TX"]
print(f"Total TX rows: {len(df)}")

# Convert 交易日期 to datetime for proper sorting
df['交易日期'] = pd.to_datetime(df['交易日期'])

# Convert 到期月份(週別) to datetime for comparison (assuming YYYYMM format)
df['到期月份_date'] = pd.to_datetime(df['到期月份(週別)'], format='%Y%m', errors='coerce')

# Group by 交易日期 and 交易時段, then keep only the row with the most recent 到期月份
filtered_df = df.groupby(['交易日期', '交易時段']).apply(
    lambda group: group.loc[group['到期月份_date'].idxmax()] if not group['到期月份_date'].isna().all() else group.iloc[0]
, include_groups=False).reset_index()

# Drop the helper column
filtered_df = filtered_df.drop('到期月份_date', axis=1)

print(f"Filtered rows: {len(filtered_df)}")
print("\nFirst few rows:")
print(filtered_df.head(10))

# Save the filtered data
filtered_df.to_csv("data/filtered_tx_2024.csv", index=False, encoding="utf-8")
