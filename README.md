# lil' bank buddy

Your friendly neighborhood buddy for all things bank accounts! This Python project helps you import, analyze, and report on your bank account transactions using CSV exports and SQLite, with a focus on automation and clear, actionable insights.

## Features
- Import transactions from CSV exports (e.g., USAA, other banks)
- **Currently supports CSV format only** (the most common and widely available export format)
- Store and query all data in a local SQLite database
- Analyze spending, deposits, categories, and trends
- Generate clear Markdown reports with key stats and insights
- Modular Python code for easy extension

## Directory Structure
```
lil-bank-buddy/
├── data/                        # All data files (CSV exports, SQLite DB, etc.)
├── reports/                     # Generated markdown or other reports
├── src/                         # All Python source code
├── tests/                       # Unit tests
├── requirements.txt
├── USAA_Transaction_Caching_Guide.md
└── README.md
```

## Quick Start

### 1. (Optional) Install Homebrew (macOS users)
If you don't have [Homebrew](https://brew.sh/) installed, run:
```zsh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. (Recommended) Install a Python version manager
We recommend [pyenv](https://github.com/pyenv/pyenv) for managing Python versions:
```zsh
brew install pyenv
pyenv install 3.11.9  # or your preferred version
pyenv global 3.11.9
```

### 3. Set up your virtual environment
```zsh
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies and the CLI tool
```zsh
pip install -e .
```
This will install all dependencies and make the `buddy` CLI available in your environment.

### 5. Place your CSV exports in `data/bank-exports/`.

### 6. Import data into the database
```zsh
python src/import_usaa_csvs.py
```

### 7. Generate a Markdown report using the CLI
```zsh
buddy report
```

### 8. View your report in the `reports/` directory.

---

## CLI Usage

After installation, you can use the `buddy` command from anywhere in your environment:

- Generate a report:
  ```zsh
  buddy report
  ```

You can extend the CLI with more commands as needed.

## License
MIT

---
**lil' bank buddy: Your friendly neighborhood buddy for all things banking!**
