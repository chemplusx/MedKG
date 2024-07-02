# ETL Pipeline Scripts for Knowledge Graph Database

This repository contains scripts for ETL pipelines designed to extract data from multiple sources, transform it according to specific schemas, and load it into a Knowledge Graph database. Each source has its own dedicated ETL script located in its respective folder within this repository.

## Sources

1. **Biomarkers Data**
   - ETL script location: `biomarkers_data/**.py`
   - Description: Extracts biomarkers data from its source, transforms it into a format suitable for the Knowledge Graph schema, and loads it into the database.

2. **DrugBank Data**
   - ETL script location: `drugbank_data/**.py`
   - Description: Extracts drug data from DrugBank, performs necessary transformations, and inserts it into the Knowledge Graph database.

3. **Metabolite Data**
   - ETL script location: `metabolite_data/**.py`
   - Description: Extracts metabolite information, processes it to align with the Knowledge Graph structure, and loads it into the database.

4. **Prime KG Data**
   - ETL script location: `prime_kg/**.py`
   - Description: Extracts specific data related to Prime KG, transforms it as required, and integrates it into the Knowledge Graph database.

5. **TDD (Target Drug Discovery) Data**
   - ETL script location: `tdd_data/**.py`
   - Description: Extracts data pertinent to Target Drug Discovery, applies transformations to fit the Knowledge Graph schema, and loads it into the database.

## Requirements

- Python 3.x
- Dependencies listed in each source's `requirements.txt` file.

## Usage

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/chemplusx/MedKG.git
   cd MedKG

2. **Install Dependencies:**

    ```bash
        pip install -r requirements.txt

3. **Setup Environment Variables**

    Setup the below environment variables as per the document structure

    ```bash
        export MEDKG_DATA=<PATH TO Data Files>
    ```

    eg. export MEDKG_DATA=/home/ubuntu/workspace/MedKG/data

4. **Run ETL Scripts:**
    
    Each source directory (biomarkers, drugbank, metabolite, prime_kg, tdd_data) contains a Python script (etl_xxx.py) for its respective ETL pipeline.

    * Navigate to the directory of the source whose data you want to process.
    * Execute the ETL script:
    
    ```bash
    python etl_xxx.py
    
5. **Verify Data in Knowledge Graph:**
    After running the ETL scripts, verify that the data has been successfully loaded into the Knowledge Graph database.

## Notes

* Ensure that you have the necessary access credentials and permissions to interact with the Knowledge Graph database.
* Modify each ETL script (etl_xxx.py) as per your specific database configuration and schema requirements.


## Contributing
Feel free to fork this repository and submit pull requests to contribute improvements or additional ETL scripts.