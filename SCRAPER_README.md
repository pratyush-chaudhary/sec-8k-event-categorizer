# Minimal SEC 8-K Scraper

A lightweight tool for downloading 8-K filings from the SEC EDGAR database.

## Features

- Downloads 8-K filings for any company by CIK
- Organizes filings into structured directories
- Rate-limited to comply with SEC requirements
- Popular company shortcuts included

## Usage

### List Popular Companies
```bash
python scrape_8k_filings.py --list-companies
```

### Dry Run (Preview)
```bash
# Last 30 days for Apple
python scrape_8k_filings.py --company apple --dry-run

# Last 365 days for Tesla  
python scrape_8k_filings.py --company tesla --days 365 --dry-run

# Custom CIK and date range
python scrape_8k_filings.py --cik 320193 --start-date 2024-01-01 --end-date 2024-12-31 --dry-run
```

### Download Filings
```bash
# Download last 30 days for Apple
python scrape_8k_filings.py --company apple

# Download specific date range for Microsoft
python scrape_8k_filings.py --company microsoft --days 90 --data-dir my_data
```

## Directory Structure

Downloaded filings are organized as:
```
data/
├── [CIK]/
│   └── [CIK]_[DATE]_[ACCESSION]_8k/
│       ├── metadata.json
│       └── [DATE]_[ACCESSION]_8k.txt
```

## Popular Companies

- apple: 320193
- microsoft: 789019  
- amazon: 1018724
- tesla: 1318605
- nvidia: 1045810

## Requirements

- Python 3.7+
- requests library
- Active internet connection 