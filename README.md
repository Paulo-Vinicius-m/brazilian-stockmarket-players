# CVM Public Companies - Shareholding Network Analysis

This project analyzes the network of relevant shareholders and publicly traded Brazilian corporations using open data from the Brazilian Securities and Exchange Commission (CVM - *Comissão de Valores Mobiliários*).

## Project Structure

```text
├── data/                                 # Ignored by git (downloaded via script)
│   ├── fre_cia_aberta_2025/              # Annual Reference Form (FRE) datasets
│   ├── fre_cia_aberta_2026/
│   └── meta_fre_cia_aberta/              # CVM documentation and metadata
├── download_data.py                      # Data downloader and organizer script
├── shareholding_network_analysis.ipynb   # Main network analysis notebook
├── .gitignore
└── README.md
```

## Getting Started

### 1. Environment Setup

Create and activate a virtual environment, then install required dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas networkx plotly scipy ipykernel
```

### 2. Download Data

Run the data download script to fetch and unpack the CVM Reference Form datasets into the `data/` directory:

```bash
# Download all years (2010 through 2026) and metadata:
python download_data.py

# Or download specific years only (e.g., 2025 and 2026):
python download_data.py --years 2025 2026

# Or download a range of years:
python download_data.py --years 2020-2026

# Download only documentation/metadata:
python download_data.py --meta-only
```

#### Script Options

- `--years`: Specify individual years (e.g., `2025 2026` or `25 26`) or ranges (`2010-2026`). Default: 2010 to 2026.
- `--output-dir`: Destination folder for datasets (default: `data`).
- `--skip-meta`: Skip downloading the metadata package.
- `--meta-only`: Download only the metadata documentation.
- `--keep-zips`: Keep intermediate `.zip` files after extraction (default: deleted after extract).
- `--force`: Re-download and overwrite existing datasets.
- `--dry-run`: Preview download actions without downloading files.

### 3. Run Analysis

Launch Jupyter Notebook or Jupyter Lab to run the analysis:

```bash
jupyter notebook shareholding_network_analysis.ipynb
```
