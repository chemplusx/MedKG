# ETL Pipeline Scripts for Knowledge Graph Database

This repository contains scripts for ETL (Extract, Transform, Load) pipelines designed to process data from multiple sources and populate a Knowledge Graph database. Each data source has its own dedicated ETL script located in its respective folder within this repository.

## Table of Contents

1. [Data Sources](#data-sources)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Contributing](#contributing)
7. [License](#license)

## Data Sources

The following data sources are currently supported:

| Source | Script Location | Description |
|--------|-----------------|-------------|
| Biomarkers | `biomarkers_data/etl_biomarkers.py` | Processes biomarkers data |
| DrugBank | `drugbank_data/etl_drugbank.py` | Handles drug data from DrugBank |
| Metabolite | `metabolite_data/etl_metabolite.py` | Manages metabolite information |
| Prime KG | `prime_kg/etl_prime_kg.py` | Processes Prime KG specific data |
| TDD (Target Drug Discovery) | `tdd_data/etl_tdd.py` | Handles Target Drug Discovery data |

Each script extracts data from its respective source, transforms it to align with the Knowledge Graph schema, and loads it into the database.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/chemplusx/MedKG.git
   cd MedKG
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Set up the environment variables:
   ```
   export MEDKG_DATA=<PATH_TO_DATA_FILES>
   ```
   Example:
   ```
   export MEDKG_DATA=/home/ubuntu/workspace/MedKG/data
   ```

2. Run the ETL script for the desired data source:
   ```
   python <source_directory>/etl_<source>.py
   ```
   Example:
   ```
   python biomarkers_data/etl_biomarkers.py
   ```

3. Verify that the data has been successfully loaded into the Knowledge Graph database.

## Configuration

- Ensure you have the necessary access credentials and permissions for the Knowledge Graph database.
- Each ETL script (`etl_<source>.py`) may require specific configuration. Refer to the comments within each script for details.
- Modify the scripts as needed to match your database configuration and schema requirements.

## Contributing

We welcome contributions to improve the ETL pipelines or add support for new data sources. To contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a new Pull Request

Please ensure your code adheres to our coding standards and includes appropriate documentation.

## License

MIT License

---

For more information or support, please [open an issue](https://github.com/chemplusx/MedKG/issues) on our GitHub repository.
