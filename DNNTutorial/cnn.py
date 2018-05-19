#!/usr/bin/env python3
#_*_ coding: utf-8 _*_

# realize CNN with numpy
# 『层』成为了我们最核心的组件。这是因为卷积神经网络有不同的层，而每种层的算法都在对应的类中实现。
import numpy as np

# Filter类保存了卷积层的参数以及梯度，并且实现了用梯度下降算法来更新参数。
class Filter(object):
    def __init__(self, width, height, depth):
        self.weights = np.random.uniform(-1e-4, 1e-4, (depth, height, width))


# 卷积层的实现
# 使用一个ConLayer类实现一个卷积层：初始化一个卷积层，可以在构造函数中设置卷积层的超参数
class ConLayer(object):
    def __init__(self, input_width, input_height, channel_numbers, 
                    filter_width, filter_height, filter_numbers,
                    zero_padding, stride, activator, learning_rate):
        self.input_width = input_width
        self.input_height = input_height
        self.channel_numbers = channel_numbers
        self.filter_width = filter_width
        self.filter_height = filter_height
        self.filter_numbers = filter_numbers
        self.zero_padding = zero_padding
        self.stride = stride
        # filters 
        self.filters = []
        for i in range(self.filter_numbers):
            self.filters.append(Filter(filter_width, filter_height, self.channel_numbers))
        # convolution 输出层
        self.output_width = \
            ConLayer.caculate_output_size(self.input_width, filter_width, zero_padding, stride)
        self.output_height = \
            ConLayer.caculate_output_size(self.input_height, filter_height, zero_padding, stride)
        self.output_array = np.zeros(((self.filter_numbers, self.output_height, self.output_width)))
        self.activator = activator
        self.learning_rate = learning_rate
    # 函数用来确定卷积层输出的大小
    @staticmethod
    def caculate_output_size(input_size, filter_size, zero_padding, stride):
        return (input_size - filter_size + 2 * zero_padding) / stride + 1