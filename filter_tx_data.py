import pandas as pd
from datetime import datetime
import glob

# Get all CSV files from 2017-2024
csv_files = sorted([f"data/{year}_fut.csv" for year in range(2017, 2025)])
print(f"Processing files: {csv_files}")

all_filtered_data = []

for csv_file in csv_files:
    year = csv_file.split('/')[-1][:4]
    print(f"\nProcessing {year} data...")

    df = pd.read_csv(csv_file, index_col=False, encoding="utf-8", low_memory=False)

    # Filter for TX contracts only
    df = df[df["契約"] == "TX"]
    print(f"Total TX rows for {year}: {len(df)}")

    # Convert 交易日期 to datetime for proper sorting
    df['交易日期'] = pd.to_datetime(df['交易日期'])

    # Convert 到期月份(週別) to datetime for comparison (assuming YYYYMM format)
    df['到期月份_date'] = pd.to_datetime(df['到期月份(週別)'], format='%Y%m', errors='coerce')

    # Group by 交易日期 and 交易時段, then keep only the row with the most recent 到期月份
    filtered_df = df.groupby(['交易日期', '交易時段']).apply(
        lambda group: group.loc[group['到期月份_date'].idxmin()] if not group['到期月份_date'].isna().all() else group.iloc[0]
    , include_groups=False).reset_index()

    # Drop the helper column
    filtered_df = filtered_df.drop('到期月份_date', axis=1)

    print(f"Filtered rows for {year}: {len(filtered_df)}")
    all_filtered_data.append(filtered_df)

# Merge all filtered data
print("\nMerging all filtered data...")
merged_df = pd.concat(all_filtered_data, ignore_index=True)

# Sort by date (oldest to latest) and trading session (一般 first, then 盤後)
trading_session_order = ['一般', '盤後']
merged_df['交易時段_sort'] = merged_df['交易時段'].map({session: i for i, session in enumerate(trading_session_order)})
merged_df = merged_df.sort_values(['交易日期', '交易時段_sort']).reset_index(drop=True)
merged_df = merged_df.drop('交易時段_sort', axis=1)

# Drop dates that only have '一般' session and not '盤後' session
session_counts = merged_df.groupby('交易日期')['交易時段'].apply(set)
dates_with_only_general = session_counts[session_counts == {'一般'}].index
print(f"\nDropping {len(dates_with_only_general)} dates that only have '一般' session")
merged_df = merged_df[~merged_df['交易日期'].isin(dates_with_only_general)]

print(f"\nTotal merged rows: {len(merged_df)}")
print(f"Date range: {merged_df['交易日期'].min()} to {merged_df['交易日期'].max()}")
print("\nFirst few rows:")
print(merged_df.head(10))
print("\nLast few rows:")
print(merged_df.tail(10))

# Save the merged filtered data
merged_df.to_csv("data/filtered_tx_all_years.csv", index=False, encoding="utf-8")
print(f"\nSaved merged data to: data/filtered_tx_all_years.csv")
