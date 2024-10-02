import instaloader
import os
import shutil
import csv
import sqlite3
import time
import sys

# Initialize SQLite3 database
def initialize_db():
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    # Create table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

# Function to get next pending username
def get_next_username():
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE status='Pending' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

# Function to update username status
def update_status(username, status):
    conn = sqlite3.connect('accounts.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status=? WHERE username=?", (status, username))
    conn.commit()
    conn.close()

# Function to download posts with error handling
def download_posts(username):
    try:
        L = instaloader.Instaloader()
        posts = instaloader.Profile.from_username(L.context, username).get_posts()

        for post in posts:
            try:
                L.download_post(post, username)
            except Exception as e:
                print(f"Error downloading post: {e}")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: The profile '{username}' does not exist.")
        update_status(username, 'Failed')
    except Exception as e:
        print(f"Unexpected error: {e}")
        update_status(username, 'Failed')
        return False
    return True

# Function to copy images and update CSV with error handling
def process_images(username):
    try:
        # Create images folder if it does not exist
        if not os.path.exists("images"):
            os.makedirs("images")

        # Create or open the CSV file in append mode
        with open('meta_data.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            # Include 'username' as an additional field in the CSV
            fieldnames = ['username', 'path', 'description']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if os.stat('meta_data.csv').st_size == 0:  # Write header if file is empty
                writer.writeheader()

            # Process each file in the username folder
            for filename in os.listdir(username):
                if filename.lower().endswith((".jpg", ".png", ".jpeg")):
                    img_name = os.path.splitext(filename)[0]
                    txt_file = os.path.join(username, f"{img_name}.txt")
                    
                    # Copy image to the "images" folder
                    src_img = os.path.join(username, filename)
                    dst_img = os.path.join("images", filename)
                    shutil.copy(src_img, dst_img)

                    # Initialize description to empty string
                    description = ""
                    
                    # Check if the corresponding txt file exists and is not empty
                    if os.path.exists(txt_file):
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as file:
                                description = file.read().strip()
                        except UnicodeDecodeError:
                            try:
                                with open(txt_file, 'r', encoding='latin-1') as file:
                                    description = file.read().strip()
                            except UnicodeDecodeError:
                                print(f"Could not read file {txt_file} due to encoding issues.")
                                description = ""

                    # Attempt to write to the CSV file, including the username
                    try:
                        writer.writerow({'username': username, 'path': dst_img, 'description': description})
                    except UnicodeEncodeError:
                        print(f"Could not write description for file {dst_img} due to encoding issues.")
                        writer.writerow({'username': username, 'path': dst_img, 'description': ""})

        # Remove the "username" folder and its contents after processing
        shutil.rmtree(username)
    except Exception as e:
        print(f"Error processing images for {username}: {e}")
        update_status(username, 'Failed')
        return False
    return True

if __name__ == "__main__":
    # Initialize database and check for errors
    try:
        initialize_db()
    except Exception as e:
        print(f"Failed to initialize the database: {e}")
        sys.exit(1)

    while True:
        username = get_next_username()
        if not username:
            print("No pending usernames found in the database. Exiting...")
            break

        print(f"Processing username: {username}")

        # Download posts and process images, update status accordingly
        if download_posts(username):
            if process_images(username):
                update_status(username, 'Done')
                print(f"Successfully processed {username}.")
            else:
                print(f"Failed to process images for {username}.")
                update_status(username, 'Failed')
        else:
            print(f"Failed to download posts for {username}.")
            update_status(username, 'Failed')

        # Take a 5-minute break before processing the next username
        print("Taking a 5-minute break...")
        time.sleep(300)  # 300 seconds = 5 minutes
