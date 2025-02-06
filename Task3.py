import time
import pandas as pd
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up WebDriver
driver_path = "/Users/shamdhage/Desktop/chrome-chromedriver-mac-x64/chromedriver"  # Path to ChromeDriver
service = Service(driver_path)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Uncomment to run without UI
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Path to Chrome binary
driver = webdriver.Chrome(service=service, options=options)

# Read Twitter profile links from the CSV file
df = pd.read_csv("twitter_links.csv", header=None)
twitter_list = df.iloc[:, 0].tolist()

# Twitter login credentials
EMAIL = "spare.yash.2025@gmail.com"
USERNAME = "Yash349513"
PASSWORD = "password"

def wait_for_element(xpath, timeout=5):  # Reduced timeout to 5 seconds
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return None


def get_element_text(xpath):
    try:
        return wait_for_element(xpath).text.strip()  # Extract and clean the text
    except:
        return "Not Available"

#Login to twitter
driver.get("https://x.com/i/flow/login")
print("Loaded Twitter login page")

# Enter email
email_field = wait_for_element('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
if email_field:
    email_field.send_keys(EMAIL)
    wait_for_element('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]/div/span/span').click()  # Click Next button
    print("Entered email")

# Enter username (if prompted)
time.sleep(3)
username_field = wait_for_element('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
if username_field:
    username_field.send_keys(USERNAME)
    wait_for_element('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/button/div').click()  # Click Next button
    print("Entered username")

# Enter password
password_field = wait_for_element('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
if password_field:
    password_field.send_keys(PASSWORD)
    wait_for_element('//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button/div').click()  # Click Log in button
    print("Logged in")

time.sleep(5)  # Wait for login to complete

data = []  # Empty list to store the profile data

for link in twitter_list:
    driver.get(link)  # Go to the profile link
    print(f"Scraping: {link}")
    time.sleep(5)

    # Extract profile details
    bio = get_element_text('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[3]/div/div/span')
    following = get_element_text('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[1]/a/span[1]/span')
    followers = get_element_text('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span')
    location = get_element_text('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div/span[1]/span/span')
    website = get_element_text('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div/a/span')


    entry = {
        "Profiles":link,
        "Bio": bio,
        "Following": following,
        "Followers": followers,
        "Location": location,
        "Website": website,
    }

    print(entry)
    data.append(entry)  # Append the data to the list
driver.quit()

#Entering data into SQL database


# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="yash_db"
)
cursor = conn.cursor()

# creating the table if it doesn't exist from before
cursor.execute("""
    CREATE TABLE IF NOT EXISTS twitter_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Profiles VARCHAR(255),
        Bio TEXT,
        Following VARCHAR(255),
        Followers VARCHAR(255),
        Location VARCHAR(255),
        Website VARCHAR(255)
    )
""")

# Extract column names dynamically
columns = ", ".join(data[0].keys())
placeholders = ", ".join(["%s"] * len(data[0]))
insert_query = f"INSERT INTO twitter_data ({columns}) VALUES ({placeholders})"
values = [tuple(d.values()) for d in data]

cursor.executemany(insert_query, values)
conn.commit()

print("Data is entered into MySQL")

# Close connection
cursor.close()
conn.close()



