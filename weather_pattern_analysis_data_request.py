import pandas as pd
import collections
from kong_sdk import environment_configuration
from kong_sdk import wtg, weather_source
from datetime import datetime, timedelta
environment_configuration('prod', 0)

# if __name__ == '__main__':
    
start_time = datetime(2020, 12, 31, 16)
end_time = datetime(2021, 1, 2, 16)
duration = (end_time - start_time).days
farm_id = 'CGNWF0077'
NWP_LIST = ['EC', 'WRF_BD_DTM_FARMS_GANSU_WIND_ML']
farm = wtg.Farm(farm_id)
farm_info = farm.get_wtg_list()
master_id = farm_info['master_id'].values[0]
turbine_lat = farm_info['lat'].values[0]
turbine_lon = farm_info['lon'].values[0]
turbine = wtg.Wtg(master_id, farm_id, turbine_lat, turbine_lon)
turbine_wind_speed = farm.get_wtg_data(start_time, number_of_days=duration, parameter='CLEAN_FILL_WIND_SPEED',
                                       stats='AVG', freq='1h', suggested_threads=4)
turbine_wind_power = farm.get_wtg_data(start_time, number_of_days=duration, parameter='CLEAN_FILL_ACTIVE_POWER',
                                       stats='AVG', freq='1h',suggested_threads=4)
weather_data = collections.defaultdict(list)
weather_data['OBS_WIND'] = turbine_wind_speed[master_id].values
weather_data['OBS_POWER'] = turbine_wind_power[master_id].values
for weather in NWP_LIST:
    if 'WRF' in weather:
        hours = 16
    else:
        hours = 28
    weather_2d = weather_source.get_weather_sequence(turbine_lat, turbine_lon, weather, 'WS',
                                                     start_time=start_time - timedelta(hours=hours),
                                                     number_of_days=duration, hours=24,offset=hours)
    weather_data[weather] = weather_2d.ravel().T
    weather_data[weather+'_POWER'] = turbine.windspeed_to_power(pd.Series(weather_data[weather],
                                                                          index=turbine_wind_speed.index)).values
weather_data_df = pd.DataFrame(weather_data, index=turbine_wind_speed.index)
weather_data_df.to_csv('D:\\optimization\\'+master_id+'.csv')
