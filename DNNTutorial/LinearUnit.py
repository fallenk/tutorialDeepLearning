from Perceptron import Perceptron

# difine activator
f = lambda x: x 
# 通过继承Perceptron，我们仅用几行代码就实现了线性单元。这再次证明了面向对象编程范式的强大。
class LinearUnit(Perceptron):
    # 初始化线性单元，设置输入参数的个数  
    def __init__(self, input_num):
        Perceptron.__init__(self, input_num, f)

# 捏造5个人的收入数据
def get_training_dataset():
    # 构建训练数据  
    # 输入向量列表，每一项是工作年限 
    input_vecs = [[5], [3], [8], [1.4], [10.1]]
    # 期望的输出列表，月薪，注意要与输入一一对应
    labels = [5500, 2300, 7600, 1800, 11400]
    return input_vecs, labels


# 使用数据训练线性单元 
def train_linear_unit():
    # 创建感知器，输入参数的特征数为1（工作年限）
    lu = LinearUnit(1)
    # 得到训练集
    input_vecs, labels = get_training_dataset()
    # 训练，迭代10轮, 学习速率为0.01 
    lu.train(input_vecs, labels, 10, 0.01)
    #返回训练好的线性单元 
    return lu

# 训练线性单元
if __name__ == "__main__":
    #训练得到权值，更新权重 
    linear_unit = train_linear_unit()
    # 打印训练获得的权重
    print(linear_unit)
    # 测试
    print("Work 3.4 years, monthly salary = %.2f" % linear_unit.predict([3.4]))
    print("Work 15 years, monthly salary = %.2f" % linear_unit.predict([15]))
    print('Work 1.5 years, monthly salary = %.2f' % linear_unit.predict([1.5]))  
    print('Work 6.3 years, monthly salary = %.2f' % linear_unit.predict([6.3]))

# 小结
# 事实上，一个机器学习算法其实只有两部分
# 模型 ====> 从输入特征x预测输入y的那个函数h(x)
# 目标函数 ====> 目标函数取最小(最大)值时所对应的 参数值 ，就是 模型的参数 的 最优值。
# 很多时候我们只能获得目标函数的局部最小(最大)值，因此也只能得到模型参数的 局部最优值。

# 接下来，你会用优化算法去求取目标函数的最小(最大)值。[随机]梯度{下降|上升}算法就是一个优化算法。
# 针对同一个目标函数，不同的优化算法会推导出不同的训练规则。我们后面还会讲其它的优化算法。
