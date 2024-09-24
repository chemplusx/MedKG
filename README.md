# ETL Pipeline Scripts for Knowledge Graph Database

This repository contains scripts for ETL (Extract, Transform, Load) pipelines designed to process data from multiple sources and populate a Knowledge Graph database. Each data source has its own dedicated folder containing ETL scripts and related files.

## Table of Contents

1. [Data Sources](#data-sources)
2. [Data Structure](#data-structure)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Configuration](#configuration)
7. [Contributing](#contributing)
8. [License](#license)

## Data Sources

The following data sources are currently supported:

| Source | Folder | Description |
|--------|--------|-------------|
| Biomarkers | `biomarkers_data/` | Biomarkers data processing |
| ChEBI | `chebi/` | Chemical Entities of Biological Interest |
| DO | `do/` | Disease Ontology data |
| DrugBank | `drugbank_data/` | Drug data from DrugBank |
| FoodOn | `foodon/` | Food Ontology data |
| GWAS Catalog | `gwas-catalog/` | Genome-Wide Association Studies data |
| Human Phenotype | `human_phenotype/` | Human Phenotype Ontology data |
| IntAct | `intact/` | Molecular interaction data |
| Metabolite | `metabolite_data/` | Metabolite information |
| OpenTargets | `opentargets/` | Open Targets Platform data |
| Prime KG | `prime_kg/` | Prime Knowledge Graph data |
| TDD (Target Drug Discovery) | `tdd_data/` | Target Drug Discovery data |
| UBERON | `uberon/` | Uber-anatomy ontology data |

Each folder contains all necessary datafiles and ETL scripts for its respective source.

## Data Structure

- All source data files are stored in the `data/` folder at the root of the project.
- ETL scripts and related files for each source are contained within their respective folders as listed above.

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
   export MEDKG_DATA=<PATH_TO_DATA_FOLDER>
   ```
   Example:
   ```
   export MEDKG_DATA=/home/ubuntu/workspace/MedKG/data
   ```

2. Run the ETL script for the desired data source:
   ```
   python <source_folder>/etl_<source>.py
   ```
   Example:
   ```
   python biomarkers_data/etl_biomarkers.py
   ```

3. Verify that the data has been successfully loaded into the Knowledge Graph database.

## Configuration

- Ensure you have the necessary access credentials and permissions for the Knowledge Graph database.
- Each ETL script may require specific configuration. Refer to the comments within each script for details.
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

[MIT License](https://github.com/chemplusx/MedKG/blob/master/LICENSE)

---

For more information or support, please [open an issue](https://github.com/chemplusx/MedKG/issues) on our GitHub repository.
