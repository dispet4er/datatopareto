import mysql.connector

def create_campaign(campaign_name, category_names, parameter_names, db_config_file):
    # Connect to MySQL database
    db_config = {}
    with open(db_config_file, 'r') as f:
        for line in f:
            key, val = line.strip().split('=')
            db_config[key] = val
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    # Insert campaign into MySQL
    query = "INSERT INTO campaign (campaign_name) VALUES (%s)"
    values = (campaign_name,)
    cursor.execute(query, values)

    # Get ID of inserted campaign
    campaign_id = cursor.lastrowid

    # Insert categories into MySQL
    for category_name in category_names:
        query = "INSERT INTO categories (category_name) VALUES (%s)"
        values = (category_name,)
        cursor.execute(query, values)

        # Get ID of inserted category
        category_id = cursor.lastrowid

        # Associate category with campaign in MySQL
        query = "INSERT INTO campaign_categories (id_campaign, id_category) VALUES (%s, %s)"
        values = (campaign_id, category_id)
        cursor.execute(query, values)

    # Insert parameters into MySQL
    for parameter_name in parameter_names:
        query = "INSERT INTO parameters (parameter_name) VALUES (%s)"
        values = (parameter_name,)
        cursor.execute(query, values)

        # Get ID of inserted parameter
        parameter_id = cursor.lastrowid

        # Associate parameter with campaign in MySQL
        query = "INSERT INTO campaign_parameters (id_campaign, id_parameter) VALUES (%s, %s)"
        values = (campaign_id, parameter_id)
        cursor.execute(query, values)

    # Commit changes and close database connection
    db.commit()
    cursor.close()
    db.close()