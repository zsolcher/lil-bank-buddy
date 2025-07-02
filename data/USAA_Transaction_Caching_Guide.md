# lil' bank buddy: Your Friendly Neighborhood Bank Account Buddy

This guide describes the essential workflow for keeping your bank account data organized and analyzed with lil' bank buddy, your friendly neighborhood buddy for all things banking!

### Workflow Summary
1. **Export CSVs from your bank** for each account, saving them in `data/bank-exports/`.
2. **Run a local script** to:
   - Read and merge all account CSVs.
   - Clean, deduplicate, and optionally filter for new transactions.
   - Store and analyze your data in a local SQLite database.
   - Generate a Markdown report with key insights and stats.
3. **Schedule the script** to run automatically (e.g., with `cron`).

---

## Step-by-Step Instructions

### 1. Export Transactions from Your Bank
- Log in to your bank account.
- Export recent transactions for each account as CSV files.
- Save these files in `data/bank-exports/` with consistent filenames.

### 2. Merge and Clean CSVs with Python
- Use a script to:
  - Read all CSVs in the export directory.
  - Normalize column names and formats.
  - Remove duplicates (based on Date, Description, Amount).
  - Store the cleaned data in your SQLite database for analysis.

#### Example Python Script
```python
import pandas as pd
import glob
import os

EXPORT_DIR = 'data/bank-exports/'
OUTPUT_FILE = 'data/merged_for_analysis.csv'

# Read all CSVs
all_files = glob.glob(os.path.join(EXPORT_DIR, '*.csv'))
dfs = [pd.read_csv(f) for f in all_files]

# Concatenate and drop duplicates
df = pd.concat(dfs, ignore_index=True)
df.drop_duplicates(subset=['Date', 'Description', 'Amount'], inplace=True)

df.sort_values(by='Date', inplace=True)
df.to_csv(OUTPUT_FILE, index=False)
print(f"Merged CSV written to {OUTPUT_FILE}")
```
*Adjust column names as needed to match your CSVs.*

### 3. Analyze and Report
- Use the provided Python scripts to:
  - Import the cleaned CSVs into your SQLite database.
  - Analyze your transactions for insights and trends.
  - Generate a Markdown report in the `reports/` directory.

---

## Security & Privacy Notes
- Store your data and credentials securely.
- Never share your exported files.

---

**This workflow gives you a streamlined, automated way to keep your bank account data up to date and analyzed, powered by lil' bank buddy!**
