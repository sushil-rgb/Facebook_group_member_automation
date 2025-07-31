# 📄 Facebook Group Member Scraper

This tool is designed to **automate the extraction of member data** from any public or private Facebook group using a headless browser environment (Camoufox) and Facebook's GraphQL API. It logs in using your credentials, scrolls through the group members, and saves all the information to an Excel file.

---

## ✅ Features

* 🔐 Logs into Facebook using secure credentials (stored in `.env`)
* 🍚 Reuses login sessions with stored cookies (Camoufox SQLite)
* 📄 Extracts:

  * Full name
  * Profile URL
  * Join status
  * Direct group member URL
* 🔁 Supports infinite scroll & cursor-based pagination
* 📅 Saves all extracted data to Excel
* 🕵️‍♂️ Uses real browser fingerprints and behavior (stealth scraping)

---

## 🧰 How It Works

1. Loads your Facebook email and password from `.env`
2. Logs into Facebook using Camoufox (headless/stealth browser)
3. Extracts session cookies from the local SQLite file
4. Makes GraphQL POST requests to fetch group members
5. Repeats for each page (cursor-based)
6. Saves the result to `Facebook Group Member Datasets` folder with your custom filename

---

## 📁 Output Format

The Excel file will contain the following columns:

| Name       | Join Status | group\_url                                                                                         | profile\_url                                                   |
| ---------- | ----------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| John Doe   | Joined 2 months ago      | [https://facebook.com/groups/.../user/1234567890](https://facebook.com/groups/.../user/1234567890) | [https://facebook.com/john.doe](https://facebook.com/john.doe) |
| Jane Smith | Joined 5 years ago     | ...                                                                                                | ...                                                            |

---

## ⚙️ Requirements

* Python 3.8+
* Dependencies (automatically handled if you're using `requirements.txt`)


## 📦 Files Included

* `main.py` – Entry point to start the scraper
* `scraper.py` – Contains the scraping logic
* `tools.py` – Helper functions (like random intervals, Excel writer)
* `.env` – Environment file to securely store Facebook credentials
* `user-data-dir/` – Stores persistent browser sessions and cookies
* `Facebook Group Member Datasets` – Output folder

---

# Step 1: Install requirements

pip install -r requirements.txt

# Step 2: Set your Facebook credentials inside .env

```python
FACEBOOK_EMAIL=your_email_here
FACEBOOK_PASSWORD=your_password_here
```

## 🚀 Running the Scraper

Here's how you should run the scraper:

### 🔐 First Run (Login Session)

Uncomment and run the login function to save your session:

```python
# await save_login_session(False)
```

Once logged in successfully and your cookies are saved, you can comment it out for future runs.

### 📤 Extract Members to Excel

# Step 3: Run the scraper

```python
python main.py
```

# Example inside main.py:

```python
time_interval = 8
file_name = "group name"
member_datas = await automate_members(member_url, time_interval)
return await save_to_excel(member_datas, f"{file_name} members")
```

---

## 💡 Notes

- You only need to log in once; the session will be reused from the SQLite cookie storage.
- Camoufox is stealthy enough to bypass most detection systems.
- You can adjust the scroll delay and max pages for better performance or stealth.

---

## 🎥 Video Tutorial

Watch the full step-by-step guide below:

[📺 Watch Tutorial](https://www.youtube.com/watch?v=xJXzeuaRW4A)

---

## 📞 Support

If you run into any issues or want to scrape more Facebook content (posts, comments, events), feel free to reach out.

