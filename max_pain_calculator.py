import pandas as pd
import numpy as np

def calculate_max_pain(csv_file):
    """Calculate max pain price from TXO options data"""

    # Read the CSV file with explicit handling of empty fields
    df = pd.read_csv(csv_file, na_values=['-', ''], keep_default_na=True, index_col=False)

    # Convert open interest and strike price to numeric
    df['未沖銷契約數'] = pd.to_numeric(df['未沖銷契約數'], errors='coerce').fillna(0)
    df['履約價'] = pd.to_numeric(df['履約價'], errors='coerce')

    # Filter for regular trading session (一般) and non-zero open interest
    df_filtered = df[
        (df['交易時段'] == '一般') &
        (df['未沖銷契約數'] > 0) &
        (df['履約價'].notna())
    ].copy()

    print(f"Total rows in CSV: {len(df)}")
    print(f"Open interest value counts:")
    print(df['未沖銷契約數'].value_counts().head(10))
    print(f"Rows after filtering: {len(df_filtered)}")

    if len(df_filtered) == 0:
        print("No data found with 一般 trading session. Using all non-zero open interest data...")
        df_filtered = df[
            (df['未沖銷契約數'] > 0) &
            (df['履約價'].notna())
        ].copy()
        print(f"Rows with non-zero open interest: {len(df_filtered)}")

        if len(df_filtered) == 0:
            return None

    # Generate strike range using np.arange
    min_strike = df_filtered['履約價'].min()
    max_strike = df_filtered['履約價'].max()
    strikes = np.arange(min_strike, max_strike + 100, 100)
    print(f"Strike price range: {min_strike} to {max_strike}")
    print(f"Generated strikes from {strikes[0]} to {strikes[-1]} with step 100")
    print(f"Number of strikes: {len(strikes)}")

    max_pain_values = []

    for strike in strikes:
        total_pain = 0

        # For each strike price, calculate total pain
        for _, row in df_filtered.iterrows():
            option_strike = row['履約價']
            open_interest = row['未沖銷契約數']
            option_type = row['買賣權']

            if option_type == '買權':  # Call option
                if strike > option_strike:
                    pain = (strike - option_strike) * open_interest
                else:
                    pain = 0
            elif option_type == '賣權':  # Put option
                if strike < option_strike:
                    pain = (option_strike - strike) * open_interest
                else:
                    pain = 0
            else:
                pain = 0

            total_pain += pain

        max_pain_values.append((strike, total_pain))

    # Find strike with minimum total pain
    max_pain_strike = min(max_pain_values, key=lambda x: x[1])

    print(f"\nMax Pain Analysis for TXO_20250924:")
    print(f"Max Pain Price: {max_pain_strike[0]:,.0f}")
    print(f"Total Pain at Max Pain: {max_pain_strike[1]:,.0f}")

    # Show top 10 strikes with lowest pain
    sorted_pain = sorted(max_pain_values, key=lambda x: x[1])
    print(f"\nTop 10 strikes with lowest pain:")
    for i, (strike, pain) in enumerate(sorted_pain[:10]):
        print(f"{i+1}. Strike {strike:,.0f}: Pain {pain:,.0f}")

    return max_pain_strike[0]

if __name__ == "__main__":
    max_pain_price = calculate_max_pain("/Users/johnny/Desktop/JQC/TX/data/TXO_20250923.csv")
