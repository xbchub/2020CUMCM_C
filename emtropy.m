clc
clear all
%求解授信风险因子权重：供求关系稳定性、违约概率、偿还能力
%求解突发因素风险因子：企业偿债稳定性、企业抗风险能力、企业发展前景
input('filename=')
positive_data = xlsread('filename')
save data positive_data
%% 剔除野数据，即3sigma以外数据
[nanRows, ~] = find(isnan(data));           % 找到存在NaN的行
data(nanRows, :) = [];                      % 删除存在NaN的行
miu = mean(data);         % 平均值
sigma = std(data);        % 标准差
for i = 1: size(data, 1)
    % 3sigma以外的数据赋值NaN
    for j = 1: size(data, 2)
        if (abs(data(i, j) - miu(j))) > 3 * sigma(j)
            data(i, j) = NaN;
        end
    end
end
[nanRows, ~] = find(isnan(data));           % 找到存在NaN的行
data(nanRows, :) = [];                      % 删除存在NaN的行

%% 对授信风险因子中的违约概率进行正向化
Position = [2, 3]
Type = [1, 1]
%选择违约概率和偿还能力进行正向化
positive_data(:,Position(1)) = max(Position(1))-Position(1);
positive_data(:,Position(2)) = max(Position(2))-Position(2);
%% 突发因素风险因子无需正向化

%% 对矩阵整体进行标准化
standard = repmat(sum(positive_data.*positive_data).^0.5, n, 1)
standard_data = positive_data./standard;

%根据函数求解熵权法权重
weight = entropy_m(standard_data);
disp('熵权法确定的权重为：')
disp(weight)

%% 熵权法求解权重：entropy_m
function [weight] = entropy_m(standard_data)
%计算熵权
    [n,m] = size(standard_data);
    %行向量
    row = zeros(1,m);
    for i = 1:m
        %取出对应的列指标
        column = standard_data(:,i);
        p = column/sum(column);
        % 信息熵，entropy
        entropy = -sum(p.*log(p(n)))/log(n);
        % 进一步求解信息有效值
        row(i) = 1- entropy;
    end
    %归一化，得到最终权重
    weight = row./sum(row);    
end