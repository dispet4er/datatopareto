import mysql.connector

# establish database connection
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Borntorun4569"
)

# create database
cursor = db.cursor()

# create database
cursor = db.cursor()
# cursor.execute("CREATE DATABASE call_analysis_platform")

# switch to call_analysis_platform database
cursor.execute("USE call_analysis_platform")

# #create tables
# cursor.execute("""
#     CREATE TABLE dates_list (
#       id_date INT AUTO_INCREMENT PRIMARY KEY,
#       date DATE NOT NULL,
#       weekend_dates ENUM('Weekday', 'Saturday', 'Sunday') NOT NULL
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE hours (
#       id_hour INT AUTO_INCREMENT PRIMARY KEY,
#       hour TIME NOT NULL,
#       hour_p1 TIME NOT NULL,
#       hour_p2 TIME NOT NULL
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE user (
#       id_user INT AUTO_INCREMENT PRIMARY KEY,
#       user_role ENUM('Admin', 'Manager', 'Agent') NOT NULL,
#       user_email VARCHAR(255) NOT NULL,
#       user_title VARCHAR(255),
#       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE license (
#       id_license INT AUTO_INCREMENT PRIMARY KEY,
#       id_user INT NOT NULL,
#       company_name VARCHAR(255) NOT NULL,
#       company_industry VARCHAR(255),
#       company_size ENUM('Small', 'Medium', 'Large'),
#       domain VARCHAR(255),
#       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#       FOREIGN KEY (id_user) REFERENCES user(id_user)
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE import_data (
#       id_import INT AUTO_INCREMENT PRIMARY KEY,
#       id_user INT NOT NULL,
#       file_name VARCHAR(255) NOT NULL,
#       count_of_rows INT NOT NULL,
#       count_of_valid_rows INT NOT NULL,
#       imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#       FOREIGN KEY (id_user) REFERENCES user(id_user)
#     )
# """)
#
# #create campaign table
# cursor.execute("""
# CREATE TABLE campaign (
#     id_campaign INT AUTO_INCREMENT PRIMARY KEY,
#     campaign_name VARCHAR(255) NOT NULL,
#     id_user INT NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (id_user) REFERENCES user(id_user)
# )
# """)
#
# cursor.execute("""
#     CREATE TABLE call_ (
#       id_call INT AUTO_INCREMENT PRIMARY KEY,
#       id_user INT NOT NULL,
#       date_id INT NOT NULL,
#       hour_id INT NOT NULL,
#       call_duration TIME NOT NULL,
#       call_disposition VARCHAR(255),
#       caller_name VARCHAR(255),
#       id_caller VARCHAR(255),
#       prospect_name VARCHAR(255),
#       id_prospect VARCHAR(255),
#       recording_url VARCHAR(255),
#       recording_transliteration VARCHAR(255),
#       id_campaign INT NOT NULL,
#       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#       FOREIGN KEY (id_user) REFERENCES user(id_user),
#       FOREIGN KEY (date_id) REFERENCES dates_list(id_date),
#       FOREIGN KEY (hour_id) REFERENCES hours(id_hour),
#       FOREIGN KEY (id_campaign) REFERENCES campaign(id_campaign)
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE import_calls (
#       id_import INT NOT NULL,
#       id_call INT NOT NULL,
#       PRIMARY KEY (id_import, id_call),
#       FOREIGN KEY (id_import) REFERENCES import_data(id_import),
#       FOREIGN KEY (id_call) REFERENCES call_(id_call)
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE export_data (
#       id_export INT AUTO_INCREMENT PRIMARY KEY,
#       id_user INT NOT NULL,
#       file_name VARCHAR(255) NOT NULL,
#       count_of_rows INT NOT NULL,
#       count_of_valid_rows INT NOT NULL,
#       exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#       FOREIGN KEY (id_user) REFERENCES user(id_user)
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE export_calls (
#       id_export INT NOT NULL,
#       id_call INT NOT NULL,
#       PRIMARY KEY (id_export, id_call),
#       FOREIGN KEY (id_export) REFERENCES export_data(id_export),
#       FOREIGN KEY (id_call) REFERENCES call_(id_call)
#     )
# """)
#
# # create categories table
# cursor.execute("""
# CREATE TABLE categories (
#   id_category INT AUTO_INCREMENT PRIMARY KEY,
#   category_name VARCHAR(255) NOT NULL,
#   id_campaign INT NOT NULL,
#   id_user INT NOT NULL,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   FOREIGN KEY (id_campaign) REFERENCES campaign(id_campaign),
#   FOREIGN KEY (id_user) REFERENCES user(id_user)
# )
# """)
#
# # create parameters table
# cursor.execute("""
# CREATE TABLE parameters (
#   id_parameter INT AUTO_INCREMENT PRIMARY KEY,
#   parameter_name VARCHAR(255) NOT NULL,
#   id_category INT NOT NULL,
#   id_user INT NOT NULL,
#   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#   FOREIGN KEY (id_category) REFERENCES categories(id_category),
#   FOREIGN KEY (id_user) REFERENCES user(id_user)
# )
# """)



cursor.execute("DROP DATABASE call_analysis_platform")