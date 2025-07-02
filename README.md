# lil' bank buddy

Your friendly neighborhood buddy for all things bank accounts! This Python CLI tool helps you import, analyze, and report on your bank account transactions using CSV exports and SQLite, with a focus on automation and clear, actionable insights.

## Features
- 🏦 Import transactions from CSV exports (USAA, other banks)
- 📊 Analyze spending patterns, categories, and trends  
- 📈 Generate comprehensive Markdown reports with charts
- 💰 Smart expense splitting between multiple people
- 🧠 Intelligent settlement detection
- 🚀 Modern CLI with intuitive commands
- 📁 Clean, maintainable codebase following Python best practices

## Project Structure
```
lil-bank-buddy/
├── src/                         # Source code
│   ├── cli.py                   # Main CLI entry point
│   ├── __main__.py              # Module execution support
│   ├── commands/                # CLI command modules
│   │   ├── import_cmd.py        # Import CSV data
│   │   ├── report_cmd.py        # Generate reports
│   │   └── analyze_cmd.py       # Analysis commands
│   ├── core/                    # Core business logic
│   │   ├── database.py          # Database operations
│   │   ├── analysis.py          # Transaction analysis
│   │   └── report.py            # Report generation
│   └── utils/                   # Utility functions
│       └── formatters.py        # Data formatting utilities
├── data/                        # Data files (CSV exports, SQLite DB)
├── reports/                     # Generated reports and charts
├── tests/                       # Unit tests
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── pyproject.toml              # Modern Python project config
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
buddy import
```

### 7. Generate a comprehensive Markdown report
```zsh
buddy report --person1-name "Zach" --person2-name "Samantha" --person1-percentage 60
```

### 8. View your report in the `reports/` directory.

---

## CLI Usage

After installation, you can use the `buddy` command from anywhere:

```zsh
# Get help
buddy --help

# Import CSV files from bank exports
buddy import --export-dir data/bank-exports/

# Preview what would be imported without actually importing
buddy import --dry-run

# Generate a report with custom expense splitting
buddy report --person1-name "Person A" --person2-name "Person B" --person1-percentage 60

# Analyze account data
buddy analyze --account both --days 30

# Get help for any command
buddy import --help
buddy report --help
buddy analyze --help
```

## Alternative Usage (Without Installation)

You can also run the CLI directly without installing:

```zsh
# Run from the project directory
python -m src --help
python -m src import --help
python -m src report --person1-name "Zach" --person1-percentage 60
```

## License
MIT

---
**lil' bank buddy: Your friendly neighborhood buddy for all things banking!**
