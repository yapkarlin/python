from selenium import webdriver

chrome_driver_path = "C:\\Users\carlene.yap\Documents\chromedriver.exe"
driver = webdriver.Chrome(executable_path=chrome_driver_path)

DAY_START = 3
DAY_END = 3
MONTH = "11"
YEAR = 2021
# stations_ids = {
#     "chenglu": "9114",
#     "xikeng": "5229",
#     "daohuikou": "14714",
#     "xiecun": "3112",
#     "ruoliao": "9115",
#     "andaihou": "2485",
#     "dapankeng": "5223",
#     "dapankeng_2": "2475",
#     "anmin": "3117",
#     "xiecunyi": "2472",
# }

stations_ids = {
    "dapankeng": "5223",
    "dapankeng_2": "2475",
    "anmin": "3117",
    "xiecunyi": "2472",
}

for day in range(DAY_START, DAY_END+1):
    if day < 10:
        rainfall_date = f"{YEAR}-{MONTH}-0{day}"
    else:
        rainfall_date = f"{YEAR}-{MONTH}-{day}"
    for station in stations_ids:
        driver.get(f"http://wap.lssywater.com/Info/RainReports_hour.aspx?stcd={stations_ids[station]}&tm={rainfall_date}")
        for num in range(24):
            obs_time = driver.find_element_by_xpath(f'//*[@id="form1"]/div[4]/div[2]/table/tbody/'
                                                    f'tr[{num+1}]/td[2]/div').text
            obs_rain = driver.find_element_by_xpath(f'//*[@id="form1"]/div[4]/div[2]/table/tbody/'
                                                    f'tr[{num+1}]/td[3]/div').text
            file_name = f"rainfall_{station}_{rainfall_date}.csv"
            with open(file_name, "a") as file:
                file.write(f"{obs_time}, {obs_rain}")
                file.write("\n")

# ====== Manual run specific day and station ======
# rainfall_date = "2020-12-24"
# station = "xiecunyi"
# driver.get(f"http://wap.lssywater.com/Info/RainReports_hour.aspx?stcd={stations_ids[station]}&tm={rainfall_date}")
# for num in range(24):
#     obs_time = driver.find_element_by_xpath(f'//*[@id="form1"]/div[4]/div[2]/table/tbody/tr[{num+1}]/td[2]/div').text
#     obs_rain = driver.find_element_by_xpath(f'//*[@id="form1"]/div[4]/div[2]/table/tbody/tr[{num+1}]/td[3]/div').text
#     file_name = f"rainfall_{station}_{rainfall_date}.csv"
#     with open(file_name, "a") as file:
#         file.write(f"{obs_time}, {obs_rain}")
#         file.write("\n")

driver.quit()

