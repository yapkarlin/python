import os
from datetime import datetime, timedelta
from kong_sdk.power_curve_service import get_device_power_curve
from kong_sdk.wtg import Farm
from kong_sdk import sequence
from functions_evaluation import *

WIND_FARM_ID = "CGNWF0077"
START_YEAR = 2022
START_MONTH = 3
START_DAY = 1
LAST_EVAL_HOUR = 23
TURBINE_INDEX = 0
UTC_DELTA = 8

"""
开始评估时间:2022年1月8日00时，结束时间：现实时间的前一天23时。
风速是风场平均风速，upload转功率曲线还是套用第一个风机的
文件1：upload，manual分别套功率曲线，功率曲线套用第一台风机，每天结果单独存文件。
文件2：每天统计，每天计算风速指标、功率指标（upload，manual分别套功率曲线和obs pwr对比），输出到评估文件。
文件3：文件1的所有数据合并。
"""


def find_windcsv_files(wind_farm_id):
    files_list = []
    for each_file in os.listdir(os.getcwd()):
        # to get current working directory of this script
        if (f"farm_{wind_farm_id}_fcst_wind" in each_file) & ("csv" in each_file):
            files_list.append(each_file)
    return files_list


def find_powercsv_files(wind_farm_id):
    files_list = []
    for each_file in os.listdir(os.getcwd()):
        if (f"{wind_farm_id}_power_wind" in each_file) & ("csv" in each_file):
            files_list.append(each_file)
    return files_list


def get_two_evaluate(obs, nwp):
    rmse = round(get_rmse(obs, nwp), 4)
    me = round(get_mean_err(obs, nwp), 4)
    return [rmse, me]


if __name__ == "__main__":
    start_time = datetime(START_YEAR, START_MONTH, START_DAY)  # BJT
    end_time = datetime(datetime.now().year, datetime.now().month, datetime.now().day)-timedelta(days=1) + timedelta(hours=LAST_EVAL_HOUR)
    # BJT last timing is 23LT
    tz = timedelta(hours=UTC_DELTA)
    farm_id = WIND_FARM_ID
    farm = Farm(farm_id)
    turbine_index = TURBINE_INDEX
    turbine_id = farm.get_wtg_list()['master_id'][turbine_index]
    # print(farm.get_wtg_list())
    wind_fcst_csv_file_list = find_windcsv_files(farm_id)

    # observed hourly wind speed of every wind turbine in 0077 wind farm in UTC
    speeds_obs = farm.get_wtg_data(start_time-tz, end_time-tz+timedelta(hours=1),
                                   parameter='CLEAN_FILL_WIND_SPEED', freq='60min')

    # observed hourly power of every wind turbine in 0077 wind farm in UTC
    powers_obs = farm.get_wtg_data(start_time-tz, end_time-tz+timedelta(hours=1),
                                   parameter='CLEAN_FILL_ACTIVE_POWER', freq='60min')  # UTC

    col = ['rmse_speed_upload', 'me_speed_upload', 'rmse_speed_manual', 'me_speed_manual',
           'rmse_power_upload', 'me_power_upload', 'rmse_power_curve', 'me_power_curve',
           'rmse_power_manual', 'me_power_manual']
    evaluate_frame = pd.DataFrame(index=pd.date_range(start=start_time, end=end_time, freq="D"), columns=col)
    for fcdate in pd.date_range(start=start_time, end=end_time, freq="D"):
        fcutc = fcdate - tz  # BJT
        file = f"farm_{farm_id}_fcst_wind_{fcdate.strftime('%Y%m%d')}.csv"
        evaluate = []
        if file not in wind_fcst_csv_file_list:
            print(f"Warning! {file} is missing.")
        else:
            print(f"processing {file}.")
            data = pd.read_csv(file, index_col=0)
            spd_upload = data['upload']
            spd_manual = data['manual_correct']
            pc = get_device_power_curve('WIND', turbine_id, fcutc)  # 预报时间最近的风场第一台风机的功率曲线
            data['fcst_power_curve'] = np.interp(spd_upload, pc['speeds'], pc['powers'])*0.194

            upload_power_all = sequence.get_wind_result(master_id=farm_id, attribute="POWER",
                                                        forecast_type="UPLOADED",
                                                        start_time=fcutc, length=96)
            upload_power_hour = []
            for i in range(0, 93, 4):
                selected = upload_power_all[i]/1000  # power unit in MW
                upload_power_hour.append(selected)
            data['upload_power'] = upload_power_hour

            data['manual_power'] = np.interp(spd_manual, pc['speeds'], pc['powers'])*0.194
            # data['obs_speed'] = speeds_obs.loc[fcutc:fcutc+timedelta(hours=23)].iloc[:, turbine_index].values
            data['obs_speed'] = np.nanmean(speeds_obs.loc[fcutc:fcutc + timedelta(hours=23)], 1).round(4)
            # data['obs_power'] = powers_obs.loc[fcutc:fcutc + timedelta(hours=23)].iloc[:, turbine_index].values
            # file1
            data['obs_power'] = (np.nanmean(powers_obs.loc[fcutc:fcutc + timedelta(hours=23)], 1).round(4))*0.194
            data.to_csv(f"{farm_id}_power_wind_{fcdate.strftime('%Y%m%d')}.csv")
            evaluate_list = []
            # evaluation speed
            evaluate_list.extend(get_two_evaluate(data['obs_speed'], data['upload']))
            evaluate_list.extend(get_two_evaluate(data['obs_speed'], data['manual_correct']))
            # evaluation power
            evaluate_list.extend(get_two_evaluate(data['obs_power'], data['upload_power']))
            evaluate_list.extend(get_two_evaluate(data['obs_power'], data['fcst_power_curve']))
            evaluate_list.extend(get_two_evaluate(data['obs_power'], data['manual_power']))
            evaluate_frame.loc[fcdate] = evaluate_list

    # evaluate_frame.to_csv(f"evaluation_to_{end_time.strftime('%Y%m%d')}.csv")  # file2
    evaluate_frame.to_csv(f"evaluation_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.csv")
    # concat all data in one file
    power_csv = find_powercsv_files(farm_id)
    data_all = pd.DataFrame()

    for f in power_csv:
        data = pd.read_csv(f, index_col=0)
        data_all = pd.concat([data_all, data], axis=0)
    # data_all.to_csv(f"combined_to_{end_time.strftime('%Y%m%d')}.csv")  # file3
    data_all.to_csv(f"combined_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.csv")
