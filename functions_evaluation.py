#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import math
import pandas as pd


# obs & nwp data should exclude NaN value
def get_rmse(obs, nwp):
    # print(nwp-obs)
    mse = np.square(np.subtract(obs, nwp)).mean()
    # rmse = np.sqrt(((nwp - obs) ** 2).mean())
    rmse = math.sqrt(mse)
    return rmse


def get_mean_err(obs, nwp):
    mean_err = np.mean(nwp - obs)
    return mean_err


def get_mae(obs, nwp):
    mae = np.mean(np.abs(nwp - obs))
    return mae


def get_mape(obs, nwp):
    mape = np.mean(np.abs((nwp - obs)/obs))
    return mape


# def get_ae_max(obs, nwp):
#     ae_max = np.max(np.abs(nwp - obs))
#     return ae_max

# def get_std(obs, nwp):
#     mean_err = get_err(obs, nwp)
#     std = np.sqrt(((nwp - obs - mean_err) ** 2).mean())
#     return std

# def get_mape_max(obs, nwp):
#     max_mape = max(abs(nwp - obs)/obs)
#     return max_mape

# def get_coef(obs, nwp):
#     std_obs = ((obs - obs.mean()) ** 2).mean()
#     std_nwp = ((nwp - nwp.mean()) ** 2).mean()
#     std_on = ((obs - obs.mean()) * (nwp - nwp.mean())).mean()
#     coor = std_on / np.sqrt(std_obs * std_nwp)
#     return coor
