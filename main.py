import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

# === IMPORTANT: make sure VPN is connected before running the script! ===

CHROME_DRIVER_PATH = "C:\\Users\carlene.yap\Documents\chromedriver.exe"
# s = Service(CHROME_DRIVER_PATH)
chart_types = {
    "radar": "RDCP",
    "pressure": "WESA",
    "rainfall": "GISP",
    "surface-obs": "STFC",
    "extreme": "WEAP",
    "satellite0": "CORN",
    "satellite1": "WXBL",
    "satellite2": "WXCL",
    "satellite3": "WXSP",
}
# under STFC,there are hourly max wind obs, hourly rainfall obs, and hourly temperature
# WEAP consists of extreme rainfall, strong convective winds, hail, lightning
# CORN and WXSP is satellite focusing on ocean area, not useful
# WXBL FY4A EC012 and ETCC very useful
# WXCL FY2G EVL useful

year = input("Enter year (4 digits) = ")
month = input("Enter month (2 digits) = ")
day_start = int(input("Enter start day = "))
day_end = int(input("Enter end day = "))
category = input("Enter chart types e.g. 'radar', 'pressure'? ")

driver = webdriver.Chrome(CHROME_DRIVER_PATH)

for day in range(day_start, day_end+1):
    if day < 10:
        date = f"0{day}"
    else:
        date = day
    if category == "pressure":
        driver.get(f"http://10.21.6.9:8080/product/{year}/{month}/{date}/{chart_types[category]}")
    else:
        driver.get(f"http://10.21.6.9:8080/product/{year}/{month}/{date}/{chart_types[category]}/medium")
    links = driver.find_elements_by_partial_link_text(chart_types[category])
    time.sleep(3)

    save_path = "C:\\Users\carlene.yap\Documents\Charts"
    date_folder = f"{year}{month}{date}"
    folder = os.path.join(save_path, category, date_folder)
    isExist = os.path.exists(folder)
    if not isExist:
        os.makedirs(folder)

    for link in links:
        # get individual URL link for each image
        image_link = link.get_attribute("href")
        firstpos = image_link.rfind("/")
        lastpos = len(image_link)
        image_filename = image_link[firstpos+1:lastpos]
        # reference website https://gethowstuff.com/python-extract-file-name-url-path/
        print(image_link)
        print(image_filename)

        # save individual image from link to a specific directory
        completeName = os.path.join(folder, image_filename)
        urllib.request.urlretrieve(image_link, completeName)

    time.sleep(3)

driver.quit()
