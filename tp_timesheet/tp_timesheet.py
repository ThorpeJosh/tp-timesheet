from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from datetime import datetime
import time


URL = ""
EMAIL = "" # your email address
DATE = datetime.now().strftime("%m/%d/%Y") 

def submit_timesheet(url, email, date, debug=false):

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    browser = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=options
    )

    # use browser to access desired webpage
    browser.get(URL)

    # wait a bit for elements on webpage to fully load
    browser.implicitly_wait(10)

    # find the email field element and fill your email
    email = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[1]/div/div[3]/div/div/input")
    email.send_keys(EMAIL)

    # find the date field and fill date
    date = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[2]/div/div[3]/div/div/input[1]")
    date.send_keys(DATE)
    
    if debug:
        # Capture image of top half of submission
        browser.save_screenshot("image_top.png")
        image = Image.open("image_top.png")
        image.show()

    # find and fill in live hours
    live_hours = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[3]/div/div[3]/div/div/input")
    live_hours.send_keys("8")

    # find and fill in the rest of the hours
    idle_hours = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[4]/div/div[3]/div/div/input")
    idle_hours.send_keys("0")
    training_hours = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[5]/div/div[3]/div/div/input")
    training_hours.send_keys("0")
    tool_issues = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[2]/div[6]/div/div[3]/div/div/input")
    tool_issues.send_keys("0")

    # find submit button and click submit
    submit = browser.find_element("xpath", "/html/body/div/div/div/div/div[1]/div/div[1]/div[2]/div[3]/div[1]/button/div")
    submit.click()
    browser.implicitly_wait(10)

    
    if debug:
        # Optional steps to show screenshot of submitted page
        browser.save_screenshot("image.png")
        image = Image.open("image.png")
        image.show()

    # close the browser after submitting
    browser.quit()

if __name__ == "__main__":
    run()
