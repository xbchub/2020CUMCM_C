# -*- coding: utf-8 -*-
import jieba
import pandas as pd
import os

# 对行业进行分类
dict1 = {
    # 房地产业、教育、科学研究和技术服务业、信息传输、软件和信息技术服务业、福利基金
    10: ['网络', '电子', '设备', '传媒', '设计', '检验', '科技', '电气',
         '材料', '生态', '医药', '检测', '安全', '器械', '节能', '机械',
         '维护', '律师', '生物', '通讯', '信息', '自动化', '药业', '教育'],
    # 住宿餐饮类、劳务承包、销售、物流交通、代工行业
    7: ['经营', '食品', '工贸', '劳务', '工贸', '运贸', '工程', '销售', '文化',
        '物流', '贸易', '商贸', '传播', '管理', '营销', '测绘', '发展', '石化',
        '安装', '园艺', '设施', '影城', '机电', '压缩', '图书', '环保', '餐饮',
        '家具', '汽贸', '广告', '租赁', '卫浴', '事务', '家居', '经纪', '商务',
        '产品', '清洁', '职业', '代理', '药房', '建材', '园林', '物业', '物资',
        '货运', '装饰', '建材'],
    # 皮革、有色金属冶炼和压延加工业、黑色金属冶炼和压延加工业、纺织服装、纺织业
    4: ['纸业', '塑料', '印刷', '印务', '包装', '鞋', '轮胎',
        '猕猴桃', '纺织', '五金', '制冷', '塑胶', '石材', '童装',
        '维修', '合金', '运']
}

# 对企业规模进行分类
dict2 = {
    # 较大规模或政策支持企业
    10: ['研究所', '有限公司', '有限责任', '公司', '福利院', '研究院', '中心'],
    # 中等规模企业
    7: ['站', '事务所', '合作社', '分公司', '印刷厂', '塑料厂', '印刷厂',
         '园艺场', '机械厂', '厂', '部'],
    # 小规模企业
    4: ['个体', '场', '装饰部', '经营部', '服务部', '经营部', '店', '药房', '五金店', '童装店']
}


def searchDict(words):
    industry = []
    scale = []
    for word in words:
        for key in dict1.keys():
            try:
                dict1[key].index(word)  # 无报错，在这个key对应的列表中
                industry.append(key)
                break  # 该词只可能出现在3个key对应的某一个列表，故可break
            except (ValueError):  # 捕捉到ValueError，该key的列表无该词
                continue

        for key in dict2.keys():
            try:
                dict2[key].index(word)  # 无报错，在这个key对应的列表中
                scale.append(key)
                break  # 该词只可能出现在3个key对应的某一个列表，故可break
            except (ValueError):  # 捕捉到ValueError，该key的列表无该词
                continue

    return industry, scale


def scoreCompany(filename):
    try:
        data = pd.read_excel(filename, sheet_name='企业信息')
    except:
        data = pd.read_excel(filename)

    scores = []
    flag = 0
    for row in range(data.shape[0]):
        company = data.iloc[row, 1]
        words = list(jieba.cut(company, cut_all=True))
        industry, scale = searchDict(words)

        if len(industry) == 0:
            print("企业{} {}无法匹配dict1".format(data.iloc[row, 0], words))
            flag = 1
            continue
        if len(scale) == 0:
            print("企业{} {}无法匹配dict2".format(data.iloc[row, 0], words))
            flag = 1
            continue

        industry = min(industry)
        scale = min(scale)
        score = industry * scale
        scores.append(score)
    if flag:
        return
    else:
        return pd.DataFrame({'企业评分': scores})


def analyseWord(filename):
    if not os.path.exists(filename):
        filename = './data/2.xlsx'

    score = scoreCompany(filename)
    return score
