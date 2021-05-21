# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import analyseWord


def statisticsMonth(sheet, enterprise, filename):
    """
    统计各企业每个月的数据并保存，用于选取合适的指标
    :param sheet: 附件1中的某个sheet，dataframe格式
    :param enterprise: 企业代号的范围
    :param filename: 保存的路径与文件名
    :return: None
    """
    # 删除作废发票
    sheet = sheet[~sheet['发票状态'].isin(['作废发票'])]

    # 创建字典，用于保存统计数据
    keys = ['企业代号', '开票年月', '金额', '税额', '价税合计']
    data = {key: [] for key in keys}

    # 手动遍历每个企业，用于按月统计
    for i in enterprise:
        dataEn = sheet[sheet['企业代号'] == 'E' + str(i)]
        if dataEn.empty:
            continue
        for years in [2016, 2017, 2018, 2019, 2020]:  # 共有5年的数据
            dataEnYear = dataEn[dataEn['开票日期'].dt.year == years]
            if dataEnYear.empty:
                continue
            for months in range(1, 13):  # 统计12个月的数据
                dataEnMonth = dataEnYear[dataEnYear['开票日期'].dt.month == months]
                if dataEnMonth.empty:
                    continue
                id = 'E' + str(i)  # 企业代号
                date = str(years) + '-' + str(months)  # 开票年月
                money = dataEnMonth['金额'].sum()  # 金额
                tax = dataEnMonth['税额'].sum()  # 税额
                both = dataEnMonth['价税合计'].sum()  # 价税总额
                list = [id, date, money, tax, both]

                for j in range(len(list)):  # 将这些值写入字典
                    data[keys[j]].append(list[j])

    # 字典转成dataframe来保存
    data = pd.DataFrame(data)
    data.to_excel(filename)


def statisticsErr(sheet, enterprise, filename):
    """
    统计各企业的发票作废率并保存
    :param sheet: 附件1中的某个sheet，dataframe格式
    :param enterprise: 企业代号的范围
    :param filename: 保存的路径与文件名
    :return: None
    """
    keys = ['企业代号', '发票作废率']
    errorRate = {key: [] for key in keys}
    for i in enterprise:
        dataEn = sheet[sheet['企业代号'] == 'E' + str(i)]
        if dataEn.empty:
            continue
        dataEnErr = dataEn[dataEn['发票状态'] == '作废发票']
        errorRate['企业代号'].append('E' + str(i))
        errorRate['发票作废率'].append(dataEnErr.shape[0] / dataEn.shape[0])  # 作废发票率=作废发票量/总发票数

    # 字典转成dataframe并保存
    errorRate = pd.DataFrame(errorRate)
    errorRate.to_excel(filename)


def getProfit(imports, exports, enterprise):
    """
    获取各企业的利润以及与利润相关的指标
    :param imports: 进项发票按月统计的dataframe
    :param exports: 销项发票按月统计的dataframe
    :param enterprise: 企业代号范围
    :return: 各企业各指标数据，格式为dataframe
    """
    # 对需要的指标创建字典
    keys = ['企业代号', '销项总额', '销项税率', '利润率', '2018-2019销项增长率']
    data = {key: [] for key in keys}
    imports['开票年月'] = pd.to_datetime(imports['开票年月'])  # 将字符串转化为datetime格式
    exports['开票年月'] = pd.to_datetime(exports['开票年月'])
    for i in enterprise:
        importsEn = imports[imports['企业代号'] == 'E' + str(i)]
        exportsEn = exports[exports['企业代号'] == 'E' + str(i)]
        if importsEn.empty or exportsEn.empty:
            continue
        id = 'E' + str(i)
        importsMoney = importsEn['金额'].sum()  # 进项总金额
        exportsMoney = exportsEn['金额'].sum()  # 销项总金额
        exportsTax = exportsEn['税额'].sum()  # 销项总税额
        # importsTax = importsEn['税额'].sum()    # 进项总税额
        # tax = exportsTax - importsTax           # 增值税
        exportTaxRate = exportsTax / exportsMoney  # 销项税率
        profitRate = (exportsMoney - importsMoney) / exportsMoney  # 利润率

        exportsperYear = []
        importsperYear = []
        for years in [2018, 2019]:
            exportsEnYear = exportsEn[exportsEn['开票年月'].dt.year == years]
            importsEnYear = importsEn[importsEn['开票年月'].dt.year == years]
            exportsperYear.append(exportsEnYear['金额'].sum())  # 存放2018、2019的销项总额
            importsperYear.append(importsEnYear['金额'].sum())  # 存放2018、2019的进项总额
        exportsIncreaseRate = (exportsperYear[1] - exportsperYear[0]) / exportsperYear[0]  # 2018-2019进项总额增长率
        # profitperYear = np.array(exportsperYear) - np.array(importsperYear)
        # profitIncreaseRate = (profitperYear[1] - profitperYear[0]) / (profitperYear[0])

        list = [id, exportsMoney, exportTaxRate, profitRate, exportsIncreaseRate]
        for j in range(len(list)):  # 写入字典
            data[keys[j]].append(list[j])
    return pd.DataFrame(data)


def processEnclosure(enclosure, enterprise, forceUpdate=0):
    """
    处理附件1或附件2，得到各指标并写入文件
    :param enclosure: =1选择附件1，=2选择附件2
    :param enterprise: 企业范围
    :param forceUpdate: =1强制更新指标文件，=0不强制更新
    :return: None
    """
    processPath = './dataPreprocess/' + str(enclosure) + '/'  # 要存放的文件路径
    dataPrefix = './data/' + str(enclosure)  # 要读取的文件前缀

    if not os.path.exists(processPath + '进项.xlsx'):  # 不存在进项文件，写入进项文件
        sheet1 = pd.read_excel(dataPrefix + '.xlsx', sheet_name='进项发票信息', usecols='A, C, E: H')
        statisticsMonth(sheet1, enterprise, processPath + '进项.xlsx', )

    if not os.path.exists(processPath + '销项.xlsx'):  # 不存在销项文件，写入销项文件
        sheet2 = pd.read_excel(dataPrefix + '.xlsx', sheet_name='销项发票信息', usecols='A,C,E:H')
        statisticsMonth(sheet2, enterprise, processPath + '销项.xlsx')

    if not os.path.exists(processPath + '发票作废率.xlsx'):  # 不存在发票作废率文件，写入发票作废率文件
        sheet2 = pd.read_excel(dataPrefix + '.xlsx', sheet_name='销项发票信息', usecols='A,C,E:H')
        statisticsErr(sheet2, enterprise, processPath + '发票作废率.xlsx')

    if enclosure == 1:
        if not os.path.exists(processPath + '信誉等级与违约情况.xlsx'):  # 1目录下不存在信誉文件，写入信誉文件
            grade = pd.read_excel(dataPrefix + '.xlsx', sheet_name='企业信息', usecols='A, C, D')
            grade.to_excel(processPath + '信誉等级与违约情况.xlsx')

        if not os.path.exists(processPath + 'index.xlsx') or forceUpdate:  # 1目录下不存在指标文件，写入指标文件
            grade = pd.read_excel(processPath + '信誉等级与违约情况.xlsx', usecols='B: C')  # 读取信誉等级
            errorRate = pd.read_excel(processPath + '发票作废率.xlsx', usecols='B, C')  # 读取发票作废率
            imports = pd.read_excel(processPath + '进项.xlsx', usecols='B: F')  # 读取进项月统计
            exports = pd.read_excel(processPath + '销项.xlsx', usecols='B: F')  # 读取销项月统计
            profit = getProfit(imports, exports, enterprise)  # 读取利润等指标
            # dataframe合并并写入文件
            index = profit.set_index('企业代号').join(errorRate.set_index('企业代号')).join(grade.set_index('企业代号'))
            index.to_excel(processPath + 'index.xlsx')

    elif enclosure == 2:
        if not os.path.exists(processPath + 'index.xlsx') or forceUpdate:  # 2目录下不存在指标文件，写入指标文件
            errorRate = pd.read_excel(processPath + '发票作废率.xlsx', usecols='B, C')  # 读取发票作废率
            imports = pd.read_excel(processPath + '进项.xlsx', usecols='B: F')  # 读取进项月统计
            exports = pd.read_excel(processPath + '销项.xlsx', usecols='B: F')  # 读取销项月统计
            profit = getProfit(imports, exports, enterprise)  # 读取利润等指标
            index = profit.set_index('企业代号').join(errorRate.set_index('企业代号'))  # dataframe合并
            index.to_excel(processPath + 'index.xlsx')  # 写入文件

    else:
        raise ValueError('选择了错误的附件')


def getExtraMat1(filename):
    """
    输出用于层次分析法的矩阵1
    :param filename: 输出的位置与文件名
    :return: None
    """
    if os.path.exists(filename):
        return
    if not os.path.exists('./dataPreprocess/1/index.xlsx'):
        processEnclosure(1, range(1, 124), 0)

    info = pd.read_excel('./dataPreprocess/1/index.xlsx', usecols='A, D, F, G, H')
    # 求出各信誉评级的违约率
    info['是否违约'][info['是否违约'] == '是'] = 1
    info['是否违约'][info['是否违约'] == '否'] = 0
    allInfo = info['信誉评级'].value_counts().sort_index().to_numpy()  # 得到各信誉评级的总企业量
    badInfo = np.array(info.loc[:, ['信誉评级', '是否违约']].groupby('信誉评级').sum())[:, -1]  # 得到违约企业量
    breakRate = badInfo / allInfo  # 违约率
    grades = ['A', 'B', 'C', 'D']
    info['违约率'] = 0
    for i in range(len(grades)):
        info['违约率'][info['信誉评级'] == grades[i]] = breakRate[i]
    columns = ['企业代号', '利润率', '违约率', '发票作废率']
    info.loc[:, columns].set_index('企业代号').to_excel(filename)


def getExtraMat2(filename):
    """
    输出用于层次分析法的矩阵2
    :param filename: 输出的位置与文件名
    :return: None
    """
    if os.path.exists(filename):
        return
    if not os.path.exists('./dataPreprocess/2/index.xlsx'):
        processEnclosure(1, range(124, 426), 0)

    info = pd.read_excel('./dataPreprocess/2/index.xlsx', usecols='A, D, E')
    info['行业评分'] = analyseWord.analyseWord('./dataPreprocess/2/企业信息.xlsx')
    info['债比率'] = 1 / (1 - info['利润率'])
    keys = ['企业代号', '行业评分', '债比率', '2018-2019销项增长率']
    info.loc[:, keys].set_index('企业代号').to_excel(filename)


if __name__ == '__main__':
    processEnclosure(1, range(1, 124), 1)
    # processEnclosure(2, range(124, 426), 0)
    # getExtraMat1('./extraMat/1.xlsx')
    # getExtraMat2('./extraMat/2.xlsx')
