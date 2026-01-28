import pandas as pd
import os
import sys
from datetime import datetime

# Import the generator
sys.path.append('.')
from demo_excel_generator import ForexSignalGenerator

def verify_csv_structure():
    print("Running verification test for MT4 CSV structure...")

    # Run the generator
    generator = ForexSignalGenerator()
    generator.run_demo(num_signals=5)

    csv_path = "signal_output/MT4_Signals.csv"

    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    expected_columns = [
        "Magic", "Symbol", "Signal", "EntryPrice", "StopLoss",
        "TakeProfit", "LotSize", "Confidence", "Timestamp"
    ]

    # Verify columns
    columns = list(df.columns)
    print(f"Found columns: {columns}")

    if columns != expected_columns:
        print(f"❌ Error: Column mismatch.")
        print(f"Expected: {expected_columns}")
        print(f"Found:    {columns}")
        sys.exit(1)

    print("✅ Columns match expected structure.")

    # Verify data types for the first row
    if len(df) > 0:
        row = df.iloc[0]
        confidence = row["Confidence"]
        timestamp = row["Timestamp"]

        print(f"Sample Row - Confidence: {confidence}, Timestamp: {timestamp}")

        # Verify Confidence is a float
        try:
            conf_val = float(confidence)
            if not (0 <= conf_val <= 1.0):
                print(f"⚠️ Warning: Confidence value {conf_val} is out of expected range [0, 1]. Generator produces [0.75, 0.95].")
        except ValueError:
             print(f"❌ Error: Confidence value '{confidence}' is not a valid number.")
             sys.exit(1)

        # Verify Timestamp is a valid date string
        try:
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"❌ Error: Timestamp '{timestamp}' is not in expected format YYYY-MM-DD HH:MM:SS")
            sys.exit(1)

        print("✅ Data types verified.")

    print("🎉 Verification Successful! The CSV structure is compatible with GenX Gold Master EA.")

if __name__ == "__main__":
    verify_csv_structure()
