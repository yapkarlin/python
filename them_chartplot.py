import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import os

SAVE_PATH = "C:\\Users\carlene.yap\Documents\Charts\daily_temp"

df = pd.read_excel("CGNWF0077_EC_tmp_201911_202001.xlsx")
columns_name = df.columns.tolist()
hours = columns_name[1:]
total_date_rows = df.shape[0]

for day in range(total_date_rows):
    date_temp_list = df.loc[day].tolist()
    plot_date = str(date_temp_list[0]).split(" ")[0]
    temperature = date_temp_list[1:]
    image_filename = f"day_{plot_date}_temp_plot_CGNWF0077.png"
    print(f"processing {image_filename} ...")
    complete_path_name = os.path.join(SAVE_PATH, image_filename)

    plt.figure(figsize=(10, 6))
    plt.title(plot_date)
    plt.minorticks_on()
    plt.grid(visible=True, which='major',color="#D3D3D3")
    plt.xlabel('Hour of the day (BJT)', fontsize=10)
    plt.xticks(rotation=45)
    plt.ylabel('Temperature (deg C)', fontsize=10)
    plt.plot(hours, temperature)
    plt.savefig(complete_path_name)
    plt.close()
