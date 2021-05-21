import os
import numpy as np
import pandas as pd
from sklearn import metrics
import joblib
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from SVM import SVM


def getData(filename, ABC):
    """
    获取数据与标签用于训练
    :param filename: 文件路径与文件名
    :param ABC: =0为第一次训练，用于ABC与D的分类；=1为第二次训练，用于A与BC的分类
    :return: 数据与标签
    """
    sourceData = pd.read_excel(filename)
    if ABC:
        sourceData = sourceData[~(sourceData['信誉评级'] == 'D')]
    # sourceData = drop3sigma(sourceData)
    data = sourceData.loc[:, '销项总额': '发票作废率']
    label = sourceData['信誉评级']
    if ABC:
        label[label == 'A'] = 1
        label[label == 'B'] = 0
        label[label == 'C'] = 0
    else:
        label[label == 'A'] = 1
        label[label == 'B'] = 1
        label[label == 'C'] = 1
        label[label == 'D'] = 0

    return np.array(data), np.array(label, dtype=int).transpose()


def drop3sigma(data):
    """
    依据3sigma原则丢弃差异过大的数据
    :param data: 输入数据，为DataFrame
    :return: 输出数据，为DataFrame
    """
    std = data.std()
    mean = data.mean()
    columns = data.columns.tolist()[1: 6]
    highest = mean + 3 * std
    lowest = mean - 3 * std

    # 循环得到[miu - 3 * sigma, miu + 3 * sigma]范围的数
    for column in columns:
        data = data[(data[column] < highest[column]) & (data[column] > lowest[column])]

    return data


def dataPreprocess(data, label):
    """
    数据标准化并划分训练集测试集
    :param data: 输入数据
    :param label: 输入标签
    :return: 训练集数据、测试集数据、训练集标签、测试集标签
    """
    preproMethod = preprocessing.StandardScaler()
    # preproMethod = preprocessing.Normalizer()
    data = preproMethod.fit_transform(data)
    trainData, testData, trainLabel, testLabel = train_test_split(
        data, label, test_size=0.1, random_state=10)
    return trainData, testData, trainLabel, testLabel


def train(kernel, model, trainData, trainLabel, forceTrain):
    trainer = SVM(kernel, trainData, trainLabel)
    if forceTrain or not os.path.exists(model):
        trainer.learnParams()
        trainer.trainSVM(model)
    trainer.crossValidation()


def test(model, testData, testLabel):
    clf = joblib.load(model)
    testPredict = clf.predict(testData)
    print(metrics.classification_report(testLabel, testPredict))
    print(metrics.confusion_matrix(testLabel, testPredict))


def main():
    forceTrain = 1

    # 第一次训练，分类ABC与D
    data, label = getData('./dataPreprocess/1/index.xlsx', ABC=False)
    trainData, testData, trainLabel, testLabel = dataPreprocess(data, label)
    kernel = 'rbf'
    modelFile = './model/firstTrain.pkl'
    # 开始训练
    print('> start first training')
    train(kernel, modelFile, trainData, trainLabel, forceTrain)
    # 测试集测试
    test(modelFile, testData, testLabel)

    # 第二次训练，分类A与BC
    data, label = getData('./dataPreprocess/1/index.xlsx', ABC=True)
    trainData, testData, trainLabel, testLabel = dataPreprocess(data, label)
    kernel = 'rbf'
    modelFile = './model/secondTrain.pkl'
    # 开始训练
    print('> start second training')
    train(kernel, modelFile, trainData, trainLabel, forceTrain)
    # 测试集测试
    test(modelFile, testData, testLabel)


if __name__ == '__main__':
    main()
