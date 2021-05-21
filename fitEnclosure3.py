# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def getData(filename):
    # 读取数据并拆成三个矩阵，逐个拟合
    data = pd.read_excel(filename, header=None)
    data = np.array(data.iloc[2:, :], dtype=float)  # 去除表头
    dataA = data[:, [0, 1]]
    dataB = data[:, [0, 2]]
    dataC = data[:, [0, 3]]
    return dataA, dataB, dataC


def func(x, a, b, c):
    # 自定义函数形式
    return a * np.log(b * x) + c


def smooth(x, y, lowest, highest):
    # 将曲线变得平滑
    xnew = np.arange(lowest, highest, 0.001)
    smoothFunc = interpolate.interp1d(x, y, kind='cubic')
    ynew = smoothFunc(xnew)
    return xnew, ynew


def fitCurve(xn, yn):
    # 拟合曲线
    popt, pcov = curve_fit(func, xn, yn)
    [a, b, c] = popt
    curve = "y = {:.5f} * ln({:.5f} * x) + {:.5f}".format(a, b, c)
    yvals = func(xn, a, b, c)
    return yvals, curve


def process(data, i):
    plotPoint(data[:, 0], data[:, 1], i)
    P, L = smooth(data[:, 0], data[:, 1], 0.04, 0.15)
    Lvals, curve = fitCurve(P, L)
    letter = ['A', 'B', 'C']
    str = letter[i - 1] + ': ' + curve
    plotCurve(P, Lvals, str)


def plotPoint(x, y, i):
    plt.subplot(1, 3, i)
    plt.plot(x, y, 'o')
    plt.xlabel('P')
    plt.ylabel('L')


def plotCurve(x, y, text):
    plt.plot(x, y, 'r')
    plt.title(text)
    plt.legend(['true', 'fit'])


def main():
    dataA, dataB, dataC = getData('./data/3.xlsx')
    process(dataA, 1)
    process(dataB, 2)
    process(dataC, 3)
    plt.show()


if __name__ == '__main__':
    main()
