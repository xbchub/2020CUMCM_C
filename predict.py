# -*- coding: utf-8 -*-
import joblib
import pandas as pd
import numpy as np
from sklearn import preprocessing


def getFirstData(filename):
    sourceData = pd.read_excel(filename)
    sourceData['2018-2019销项增长率'][np.isinf(sourceData['2018-2019销项增长率'])] = 0
    id = np.array(sourceData['企业代号'])
    data = np.array(sourceData.loc[:, '销项总额': '发票作废率'])
    preproMethod = preprocessing.StandardScaler()
    # input_data = preprocessing.Normalizer().fit_transform(input_data)
    data = preproMethod.fit_transform(data)
    return id, data


def getSecondData(filename, firstLabel):
    sourceData = pd.read_excel(filename)
    sourceData['2018-2019销项增长率'][np.isinf(sourceData['2018-2019销项增长率'])] = 0
    goodIndex = firstLabel['预测结果'] == '1'
    data = sourceData[goodIndex]
    id = np.array(data['企业代号'])
    data = np.array(data.loc[:, '销项总额': '发票作废率'])
    preproMethod = preprocessing.StandardScaler()
    # preproMethod = preprocessing.Normalizer()
    data = preproMethod.fit_transform(data)
    return id, data


def predict(model, id, data, times):
    clf = joblib.load(model)
    result = clf.predict(data)
    label = pd.DataFrame({'企业代号': id, '预测结果': result})
    if times == 1:
        label['预测结果'][label['预测结果'] == 0] = '低优先级'
        label['预测结果'][label['预测结果'] == 1] = '1'
    elif times == 2:
        label['预测结果'][label['预测结果'] == 0] = '中优先级'
        label['预测结果'][label['预测结果'] == 1] = '高优先级'
    else:
        raise ValueError('times设定错误')
    return label


def mergeLabel(firstLabel, secondLabel, filename):
    firstLabel = firstLabel[firstLabel['预测结果'] == '低优先级']
    label = pd.concat([firstLabel, secondLabel])
    label = label.sort_values(by='企业代号', ascending=True).set_index('企业代号')
    label.to_excel(filename)


def main():
    filename = './dataPreprocess/2/index.xlsx'
    # 第一次预测，分类出低优先级
    idFirst, data = getFirstData(filename)
    firstLabel = predict('./model/firstTrain.pkl', idFirst, data, times=1)

    # 第二次预测，分类高优先级与中优先级
    idSecond, data = getSecondData(filename, firstLabel)
    secondLabel = predict('./model/secondTrain.pkl', idSecond, data, times=2)

    # 合并预测结果，写入指定文件
    mergeLabel(firstLabel, secondLabel, './result/2.xlsx')


if __name__ == '__main__':
    main()
