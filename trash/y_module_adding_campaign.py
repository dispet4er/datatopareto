import mysql.connector
from mysql.connector import errorcode
from y_db_config import db_config

# establish database connection
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="call_analysis_platform"
    )
    cursor = db.cursor()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

def create_campaign(campaign_name, category_names, parameter_names):
    try:
        # insert campaign name into the campaign table
        add_campaign_query = "INSERT INTO campaign (campaign_name, id_user) VALUES (%s, %s)"
        campaign_data = (campaign_name, 1) # assuming user ID 1 is creating the campaign
        cursor.execute(add_campaign_query, campaign_data)
        campaign_id = cursor.lastrowid

        # insert category names into the Categories table
        category_ids = []
        for category_name in category_names:
            add_category_query = "INSERT INTO Categories (category_name, id_campaign, id_user) VALUES (%s, %s, %s)"
            category_data = (category_name, campaign_id, 1) # assuming user ID 1 is creating the categories
            cursor.execute(add_category_query, category_data)
            category_ids.append(cursor.lastrowid)

        # insert parameter names into the parameters table
        for parameter_name in parameter_names:
            for category_id in category_ids:
                add_parameter_query = "INSERT INTO parameters (parameter_name, id_category, id_user) VALUES (%s, %s, %s)"
                parameter_data = (parameter_name, category_id, 1) # assuming user ID 1 is creating the parameters
                cursor.execute(add_parameter_query, parameter_data)

        db.commit()
        print("Campaign created successfully.")

    except mysql.connector.Error as err:
        print("Error while creating campaign: ", err)

# example usage
create_campaign("Test Campaign", ["Category 1", "Category 2"], ["Parameter 1", "Parameter 2"])