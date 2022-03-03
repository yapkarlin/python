import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kong_sdk.wtg import Farm

WIND_FARM_ID = "CGNWF0077"
YEAR = 2021
MONTH = 10
DAY = 1
THRESHOLD = 5.5

if __name__ == '__main__':

    # Get wind farm's hourly wind speed from kong_sdk in UTC and save into a csv file
    start_time = datetime(YEAR, MONTH, DAY)  # BJT
    if MONTH == 12:
        end_time = datetime(YEAR + 1, 1, DAY) # BJT
    else:
        end_time = datetime(YEAR, MONTH + 1, DAY)
    tz = timedelta(hours=8)
    farm = Farm(WIND_FARM_ID)
    turbines_obs_speeds = farm.get_wtg_data(start_time - tz, end_time - tz,
                                            parameter='CLEAN_FILL_WIND_SPEED', freq='60min')
    hourly_obs_speed = turbines_obs_speeds.mean(axis=1).round(4)
    hourly_obs_speed.to_csv(f'hourly_wind_{YEAR}_{MONTH}_{WIND_FARM_ID}.csv')
    data = pd.read_csv(f"hourly_wind_{YEAR}_{MONTH}_{WIND_FARM_ID}.csv", header=None)
    data.rename(columns={0: 'datetime_utc', 1: 'obs_speed'}, inplace=True)
    data.to_csv(f"obs_speed_{YEAR}_{MONTH}_{WIND_FARM_ID}.csv", index=False)

    # read hourly wind speed csv file and filter to get only rows with speed above a threshold
    df = pd.read_csv(f"obs_speed_{YEAR}_{MONTH}_{WIND_FARM_ID}.csv")
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"])
    df1 = df.loc[df["obs_speed"] >= THRESHOLD]

    # find time difference between rows of datetime_utc, convert to minutes
    # index position of all datetime with wind above threshold: minute_diff.index
    minute_diff = df1.datetime_utc.diff().apply(lambda x: x / np.timedelta64(1, 'm')).fillna(0).astype('int64')
    count = len(minute_diff.index)

    # index position of the start of a new strong wind event, then get respective start datetime
    indices_list = minute_diff.index[minute_diff > 60].tolist()
    start = [df.datetime_utc.iloc[minute_diff.index[0]]]
    for item in indices_list:
        new_start = df.datetime_utc.iloc[item]
        start.append(new_start)

    # index position of the end of a strong wind event, then get respective end datetime
    end = []
    for num in range(count - 1):
        if minute_diff.index[num + 1] - minute_diff.index[num] > 1:
            endtime_index = minute_diff.index[num] + 1
            end.append(df.datetime_utc.iloc[endtime_index])
    end.append(df.datetime_utc.iloc[minute_diff.index[count - 1] + 1])

    # convert into dataframe and csv file, find duration of strong wind
    zipped = list(zip(start, end))
    df2 = pd.DataFrame(zipped, columns=["start_utc", "end_utc"])
    df2["duration_hr"] = (df2["end_utc"] - df2["start_utc"]).astype('timedelta64[h]')
    df2.to_csv(f"{WIND_FARM_ID}_strongwind_{YEAR}_{MONTH}.csv", index=False)
