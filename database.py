import sqlite3
import csv

# CSV file name
csv_file = 'usernames.csv'
# SQLite3 database file name
db_file = 'accounts.db'

def create_database_from_csv(csv_file, db_file):
    # Connect to SQLite3 database (creates file if not exists)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            status TEXT DEFAULT 'Pending'
        )
    ''')

    # Read the CSV file and insert data into the table
    with open(csv_file, 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        # Print out the field names to debug the issue
        print(f"CSV Headers: {reader.fieldnames}")

        # Normalize column names to remove any extra whitespace
        headers = [header.strip() for header in reader.fieldnames]
        if 'Name' not in headers or 'username' not in headers:
            print("CSV headers do not match expected names ('Name' and 'username'). Please check the CSV file.")
            return

        # Track usernames to prevent duplicate insertions
        existing_usernames = set()
        cursor.execute("SELECT username FROM users")
        existing_usernames.update([row[0] for row in cursor.fetchall()])

        new_users = []  # List to hold new users for batch insertion

        for row in reader:
            # Strip whitespace from keys and values to avoid KeyError
            row = {key.strip(): value.strip() for key, value in row.items()}
            username = row['username']

            # Skip if username is already in the database or in the new users list
            if username in existing_usernames or username in [user[1] for user in new_users]:
                print(f"Skipping duplicate username: {username}")
                continue

            # Add username to the new users list and track it in the existing_usernames set
            if username:  # Ensure username is not empty
                new_users.append((row['Name'], username, 'Pending'))
                existing_usernames.add(username)

    # Perform batch insert for new users only
    if new_users:
        try:
            cursor.executemany('''
                INSERT INTO users (name, username, status) 
                VALUES (?, ?, ?)
            ''', new_users)
            print(f"{len(new_users)} new users added to the database.")
        except sqlite3.IntegrityError as e:
            print(f"Integrity error while inserting new users: {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"Database '{db_file}' updated successfully with data from '{csv_file}'.")

# Create or update the database from the CSV file
create_database_from_csv(csv_file, db_file)
