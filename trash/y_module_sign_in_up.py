import sqlite3

# Connect to the database
conn = sqlite3.connect('my_database.db')
c = conn.cursor()

# Create a table for user licenses
c.execute('''CREATE TABLE IF NOT EXISTS licenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE,
              password TEXT)''')

# Sign up process - add a new user to the licenses table
def sign_up(username, password):
    try:
        c.execute('''INSERT INTO licenses (username, password)
                     VALUES (?, ?)''', (username, password))
        conn.commit()
        print(f'Successfully signed up. Welcome, {username}!')
    except sqlite3.IntegrityError:
        print('Username already exists. Please choose another username.')

# Sign in process - validate credentials to enter the platform
def sign_in(username, password):
    c.execute('''SELECT password FROM licenses
                 WHERE username = ?''', (username,))
    result = c.fetchone()
    if result is None:
        print('Username not found. Please sign up first.')
    elif password == result[0]:
        print(f'Welcome back, {username}!')
    else:
        print('Incorrect password. Please try again.')

# Example usage:
sign_up('alice', 'mypassword')
sign_in('alice', 'wrongpassword')
sign_in('bob', 'mypassword')
sign_up('alice', 'newpassword')
sign_in('alice', 'newpassword')

# Close the database connection when done
conn.close()