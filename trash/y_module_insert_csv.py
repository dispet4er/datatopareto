import csv
import mysql.connector
from datetime import datetime
from typing import Dict

def insert_csv_data(file: str, db_config: Dict[str, str]):
    # Open CSV file
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        # Connect to MySQL database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # Loop through CSV rows and insert into database
        for row in csv_reader:
            # Parse CSV data and format for MySQL
            date_str = row[0]
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            hour = datetime.strptime(row[1], '%H:%M:%S').time()
            call_duration = datetime.strptime(row[2], '%H:%M:%S').time()
            call_disposition = row[3]
            caller_name = row[4]
            id_caller = row[5]
            prospect_name = row[6]
            id_prospect = row[7]
            recording_url = row[8]
            recording_transliteration = row[9]
            id_campaign = int(row[10])

            # Insert data into MySQL
            query = "INSERT INTO call (date, hour, call_duration, call_disposition, caller_name, id_caller, prospect_name, id_prospect, recording_url, recording_transliteration, id_campaign) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (date, hour, call_duration, call_disposition, caller_name, id_caller, prospect_name, id_prospect, recording_url, recording_transliteration, id_campaign)
            cursor.execute(query, values)

        # Commit changes and close database connection
        db.commit()
        cursor.close()
        db.close()