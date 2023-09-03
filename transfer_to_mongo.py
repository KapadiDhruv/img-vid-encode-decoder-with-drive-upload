import json
import os
from pymongo import MongoClient
from os.path import exists
from dotenv import load_dotenv
load_dotenv()

mongo_url = os.environ.get('MONGO_URL')
with open("sub_list.csv", "r") as f_subreddits:
    for sub in f_subreddits:
        sub = sub.strip()

        local_path = f'encoded-data/{sub}'

        # Check if the JSON file exists
        json_file_path = f'{local_path}/file_links.json'

        if not exists(json_file_path):
            print(f'JSON file "{json_file_path}" does not exist.')
        else:
            myclient = MongoClient(f"{mongo_url}")

            # Extract the database name from the MongoDB URL
            url_parts = mongo_url.split('/')
            database_name = url_parts[-1]

            # Access the database
            db = myclient[database_name]

            # Access the collection
            collection_name = sub
            collection = db[collection_name]

            # Load JSON data from the file
            with open(json_file_path) as file:
                file_data = json.load(file)

                if isinstance(file_data, list):
                    # Insert multiple documents if it's a list
                    result = collection.insert_many(file_data)
                    print(f'Inserted {len(result.inserted_ids)} documents.')
                elif isinstance(file_data, dict):
                    # Insert a single document if it's a dictionary
                    result = collection.insert_one(file_data)
                    print(f'Inserted document with _id: {result.inserted_id}')
                else:
                    print('Invalid JSON data format.')
