from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
import os
import csv

# Nebula Graph connection configuration
config = Config()
config.max_connection_pool_size = 10
connection_pool = ConnectionPool()
connection_pool.init([('192.168.0.115', 9669)], config)

# Create a session to execute queries
session = connection_pool.get_session('root', 'nebula')

DATA_DIR = os.environ.get('MEDKG_DATA')
if DATA_DIR is None:
    DATA_DIR = os.getcwd()

# Read the CSV data and insert into Nebula Graph
with open(DATA_DIR + 'nodes.csv', 'r') as file:
    # next(file)  # Skip the header row
    n = 0
    tot = 7959
    reader = csv.DictReader(file)
    for row in reader:
        if n%10000 ==0:
            print("Done by ", (n/tot)*100)
        n+=1
        node_index = row['node_index']
        node_id = row['node_id'].replace('"', '\\"')
        node_type = row['node_type'].replace('"', '\\"')
        node_name = row['node_name'].replace('"', '\\"')
        node_source = row['node_source'].replace('"', '\\"')

        if node_type == "disease" and ('grouped' not in node_source):
            query = f"use prime_kg; upsert vertex on DISEASE \"{node_id}\" set uuid = \"{node_id}\";"
            # session.execute(query)
        elif node_type == "drug":
            
            query = f"use prime_kg; upsert vertex on DRUG \"{node_id}\" set uuid = \"{node_id}\";"
            if node_id == "DB09130":
                print(query)
                result = session.execute(query)
                print("Resuilt: ", result)
            # else:
            #     session.execute(query)