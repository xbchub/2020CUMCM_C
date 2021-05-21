# -*- coding: utf-8 -*-
import numpy as np
from sklearn.svm import SVC
from sklearn import metrics
import joblib
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score


class SVM:
    def __init__(self, kernel, trainData, trainLabel):
        """
        :param kernel: 使用的内核类型
        :param trainData: 训练集数据
        :param trainLabel: 训练集标签
        """
        self.trainData = trainData
        self.trainLabel = trainLabel
        self.clf = SVC(kernel=kernel, C=1.0, gamma=0.01, shrinking=True, tol=0.001)

    def trainSVM(self, modelFile):
        self.clf.fit(self.trainData, self.trainLabel)
        joblib.dump(self.clf, modelFile)
        trainResult = self.clf.predict(self.trainData)
        print(metrics.classification_report(self.trainLabel, trainResult))

    def learnParams(self):
        rangeC = np.logspace(-2, 10, 13)
        rangeGamma = np.logspace(-9, 3, 13)
        param_grid = dict(gamma=rangeGamma, C=rangeC)
        cv = StratifiedShuffleSplit(n_splits=5, test_size=0.1, random_state=20)
        grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv, n_jobs=-1)
        grid.fit(self.trainData, self.trainLabel)
        self.clf.set_params(C=grid.best_params_['C'], gamma=grid.best_params_['gamma'])
        print("Best parameters: {}, with a score of {:.2f}".format(
            grid.best_params_, grid.best_score_))
        # self.drawParams(grid, rangeC, rangeGamma)

        # def plotParams(self, grid, rangeC, rangeGamma):
        #     scores = grid.cv_results_['mean_test_score'].reshape(len(rangeC), len(rangeGamma))
        #     plt.imshow(scores, interpolation='nearest')
        #     plt.xlabel('gamma')
        #     plt.ylabel('C')
        #     plt.show()

    def crossValidation(self):
        # 十折交叉验证
        cv = ShuffleSplit(n_splits=10, test_size=0.1, random_state=20)
        scores = cross_val_score(self.clf, self.trainData,
                                 self.trainLabel, cv=cv, scoring='accuracy')
        print(scores)
        print("Accuracy: {:.2f} ± {:.2f}".format(scores.mean(), scores.std()))
