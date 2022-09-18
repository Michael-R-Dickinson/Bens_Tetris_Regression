import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def load_data(path):
    df = pd.read_csv(path, sep="\t")
    df.columns = df.columns.str.lower()
    df.dropna(inplace=True)

    df["propper_date"] = pd.to_datetime(df["played"])
    df["dayssincestart"] = (
        df["propper_date"] - df["propper_date"].iloc[0]).dt.total_seconds() / (24 * 3600)

    return df


def non_linear_regression(func, xData, yData):
    popt, pcov = curve_fit(
        func,
        xData,
        yData,
        bounds=(-1000, [1000.,  1000.,  1000.]),
        check_finite=True,
        maxfev=10000,
    )

    return popt


def plot_regression(func, xData, yData, popt):
    sns.set_theme()
    plt.scatter(xData, yData, s=3, label='data',
                edgecolors="#146fa3", linewidths=1, alpha=0.5)

    xModel = np.linspace(min(xData), max(xData), 250)
    yModel = func(xModel, *popt)
    plt.plot(
        xModel, yModel, 'r-',
        label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

    plt.legend()
    plt.show()


def calculate_metrics(func, xData, yData, popt):
    AE = (func(xData, *popt)) - yData
    SE = np.square(AE)
    MSE = np.mean(SE)
    RMSE = np.sqrt(MSE)
    Rsquared = 1.0 - (np.var(AE) / np.var(yData))

    return {"RMSE": RMSE}  # , "RSquared": Rsquared}


def main(data_path, func, x, y, plot=False):
    df = load_data(data_path)
    xData, yData = df[x], df[y]
    params = non_linear_regression(
        func, xData, yData
    )

    if plot:
        plot_regression(
            func, xData, yData, params
        )

    return [params], calculate_metrics(
        func, xData, yData, params
    )
