# INSTABOT
A bot to scrape/ crawl instagram

1. First install, Requirements. (main requirement: `pip install instaloader`)
2. This creates a .csv file in the same directory, with the name `usernames.csv`, and includes the Instagram account usernames for the accounts you want to scrape.
3. Run `database.py` it will create a `.db` for that usernames.
4. Run instabot.py. It will take usernames from `.db`, scrape images and metadata, and update the status in `.db`.
5. Images will be stored in the `images` folder, and a `.csv` file will be created, containing images path and metadata.

Before running the first time. You have to link your account with it via the terminal.
`instaloader --username your-username --password your-password`
