# _ *_ coding:utf-8 _*_
# 使用神经网络完成and运算
# 感知器不仅仅能实现简单的布尔运算。它可以拟合任何的线性函数，任何线性分类或线性回归问题都可以用感知器来解决
# https://blog.csdn.net/luanpeng825485697/article/details/79009050 
from functools import reduce

# define perceptron
class Perceptron(object):
    # 初始化感知器，设置输入的参数个数，激活函数
    # 激活函数的类型为double -> double
    def __init__(self, input_num, activator):
        self.activator = activator
        # 权重向量初始化为0 
        self.weights = [0.0 for _ in range(input_num)]
        # 偏置项初始化为0  
        self.bias = 0.0
    # 打印学习到的权重、偏置项
    def __str__(self):
        return "weights\t:%s\nbias\t:%s" % (self.weights, self.bias)
    # 前向输出结果:forword,predict;参数：输入向量input_vec;aim for test
    def predict(self, input_vec):
        sum=0
        for i in range(len(input_vec)):
            sum += self.weights[i]*input_vec[i]
        predicted = self.activator(sum+self.bias)
        return predicted
    # 一次迭代，把所有的训练数据过一遍  
    def _one_iteration(self, input_vecs, labels, rate):
        # 把输入和输出打包在一起，成为样本的列表[(input_vec, label), ...]  
        # 而每个训练样本是(input_vec, label)
        samples = zip(input_vecs, labels)
        # 对每个样本，按照感知器规则更新权重
        for (input_vec, label) in samples:
            # 计算感知器在当前权重下的输出
            output = self.predict(input_vec)
            # 更新权重 
            self._update_weights(input_vec, output, label, rate)
    # 按照感知器规则更新权重
    def _update_weights(self, input_vec, output, label, rate):
        # 把input_vec[x1,x2,x3,...]和weights[w1,w2,w3,...]打包在一起 
        # 变成[(x1,w1),(x2,w2),(x3,w3),...]
        # 然后利用感知器规则更新权重
        delta = label - output
        for i in range(len(input_vec)):
            self.weights[i] = self.weights[i] + rate * delta * input_vec[i]
        # 更新bias
        self.bias = self.bias + rate*delta
    # input training data;输入训练数据：一组向量、与每个向量对应的label；以及训练轮数、学习率
    def train(self, input_vecs, labels, iterations, rate):
        for i in range(iterations):
            self._one_iteration(input_vecs, labels, rate)
    
# 定义激活函数f
def f(x):
    return 1 if x>0 else 0

# 加载样本数据集
def get_training_dataset():
    # 基于and真值表构建训练数据  
    # 构建训练数据
    # 输入向量列表
    input_vecs = [[1, 1], [0, 0], [1, 0], [0, 1]]
    # 期望的输出列表，注意要与输入一一对应
    labels = [1, 0, 0, 0]
    return input_vecs, labels

# 使用and真值表训练感知器
def train_and_perceptron():
    # 创建感知器，输入参数个数为2（因为and是二元函数），激活函数为f
    p = Perceptron(2, f)
    # 训练，迭代10轮, 学习速率为0.1
    input_vecs, labels = get_training_dataset()  # 记载样本数据集 
    p.train(input_vecs, labels, 10, 0.1)
    # 返回训练好的感知器  
    return p

if __name__=="__main__":
    # 训练and感知器
    and_perceptron = train_and_perceptron()
    # 打印训练获得的权重
    print(and_perceptron)
    # 测试
    print("1 and 1 = %d" % and_perceptron.predict([1, 1]))
    print("1 and 0 = %d" % and_perceptron.predict([1, 0]))
    print("0 and 0 = %d" % and_perceptron.predict([0, 0]))
    print("0 and 1 = %d" % and_perceptron.predict([0, 1]))