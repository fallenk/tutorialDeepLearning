#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import numpy as np
from layers.base_conv import Conv2D
from layers.fc import FullyConnect
from layers.pooling import MaxPooling, AvgPooling
from layers.softmax import Softmax
from layers.relu import Relu

import time
import struct
from glob import glob

def load_mnist(path, kind='train'):
    """Load MNIST data from path`"""
    images_path = glob('./%s/%s*3-ubyte' % (path, kind))[0]
    labels_path = glob('./%s/%s*1-ubyte' % (path, kind))[0]
    with open(labels_path, 'rb') as lbpath:
        magic, n = struct.unpack('>II',
                                 lbpath.read(8))
        labels = np.fromfile(lbpath,
                             dtype=np.uint8)

    with open(images_path, 'rb') as imgpath:
        magic, num, rows, cols = struct.unpack('>IIII',
                                               imgpath.read(16))
        images = np.fromfile(imgpath,
                             dtype=np.uint8).reshape(len(labels), 784)

    return images, labels


images, labels = load_mnist('./data/mnist')
test_images, test_labels = load_mnist('./data/mnist', 't10k')
batch_size = 64
# 定义 两个 卷积层和pool层
# 输入数据的shape, 卷积核的个数，卷积核的尺寸， 步长， 是否输出原尺寸大小
conv1 = Conv2D([batch_size, 28, 28, 1], 12, 5, 1)
relu1 = Relu(conv1.output_shape)
pool1 = MaxPooling(relu1.output_shape)
conv2 = Conv2D(pool1.output_shape, 24, 3, 1)
relu2 = Relu(conv2.output_shape)
pool2 = MaxPooling(relu2.output_shape)
fc = FullyConnect(pool2.output_shape, 10)
sf = Softmax(fc.output_shape)

# 定义epoch
for epoch in range(1):
    learning_rate = 1e-5    # 学习率
    batch_loss = 0          # 损失函数
    batch_acc = 0           # 正确率
    val_acc = 0             # 总的正确率
    val_loss = 0            # 损失率

    # train
    train_acc = 0
    train_loss = 0
    for i in range(images.shape[0] // batch_size):
        img = images[i * batch_size:(i + 1) * batch_size].reshape([batch_size, 28, 28, 1])
        label = labels[i * batch_size:(i + 1) * batch_size]
        conv1_out = relu1.forward(conv1.forward(img))
        pool1_out = pool1.forward(conv1_out)
        conv2_out = relu2.forward(conv2.forward(pool1_out))
        pool2_out = pool2.forward(conv2_out)
        fc_out = fc.forward(pool2_out)
        # print i, 'fc_out', fc_out
        batch_loss += sf.cal_loss(fc_out, np.array(label))
        train_loss += sf.cal_loss(fc_out, np.array(label))

        for j in range(batch_size):
            if np.argmax(sf.softmax[j]) == label[j]:
                batch_acc += 1
                train_acc += 1

        sf.gradient()
        conv1.gradient(relu1.gradient(pool1.gradient(
            conv2.gradient(relu2.gradient(pool2.gradient(
                fc.gradient(sf.eta)))))))

        if i % 1 == 0:
            # TO-DO 传出参数，
            fc.backward(alpha=learning_rate, weight_decay=0.0004)
            conv2.backward(alpha=learning_rate, weight_decay=0.0004)
            conv1.backward(alpha=learning_rate, weight_decay=0.0004)

            if i % 50 == 0:
                # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
                #       "  epoch: %d ,  batch: %5d , avg_batch_acc: %.4f  avg_batch_loss: %.4f  learning_rate %f" % (epoch,
                #                                                                                  i, batch_acc / float(
                #           batch_size), batch_loss / batch_size, learning_rate)
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
                      "  epoch: %d ,  batch: %5d " % (epoch, i))

            batch_loss = 0
            batch_acc = 0


    print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime()) + "  epoch: %5d , train_acc: %.4f  avg_train_loss: %.4f" % (
            epoch, train_acc / float(images.shape[0]), train_loss / images.shape[0]))

    # validation
    for i in range(test_images.shape[0] // batch_size):
        img = test_images[i * batch_size:(i + 1) * batch_size].reshape([batch_size, 28, 28, 1])
        label = test_labels[i * batch_size:(i + 1) * batch_size]
        conv1_out = relu1.forward(conv1.forward(img))
        pool1_out = pool1.forward(conv1_out)
        conv2_out = relu2.forward(conv2.forward(pool1_out))
        pool2_out = pool2.forward(conv2_out)
        fc_out = fc.forward(pool2_out)
        val_loss += sf.cal_loss(fc_out, np.array(label))

        for j in range(batch_size):
            if np.argmax(sf.softmax[j]) == label[j]:
                val_acc += 1

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "  epoch: %5d , val_acc: %.4f  avg_val_loss: %.4f" % (
        epoch, val_acc / float(test_images.shape[0]), val_loss / test_images.shape[0]))

def trainAndTest(k, wt, batch_size, epoch):
    '''
    :param k: client k 编号
    :param wt: 全局参数
    :param batch_size: 每一个batch大小
    :param epoch: 整体训练次数
    :return: 训练好的参数w， 所用训练的数据集个数
    '''


# client k
def clientUpdate(k, wt):
    '''
    :param k: client k-编号
    :param wt: 传入的全局参数
    :return: newWkt, nk: 更新后的wt, 本地训练数据集的个数
    '''
    # 1. 数据集分块 根据Pk按batch_size为B进行分块
    B = 64
    batch_size = B
    epoch = 1
    # 2. 传入参数， 训练数据(根据k进行识别编号)，测试数据, 得到返回参数
    newWkt, nk = trainAndTest(k, wt, batch_size, epoch)
    return newWkt, nk

# server excute
def server(w0 = 0):
    '''
    :param w0: 训练的参数
    :return:
    '''
    # 1. initialize w0
    # w0 = np.zeros()
    # 2. 总的全局训练次数
    t = 1
    wt = w0 # 初始化
    for _ in range(t):
        # 3. 选择一批client 集合
        # m←max(C ·K, 1): m 为c个clients和
        # St ←(random set of m clients) : 每次从m个中选取St个clients
        st = np.array([1, 2])
        listWAndnk = []

        # 客户端的训练个数
        n = 0
        for k in range(len(st)):
            # newWt为当前client k的训练所得的参数；nk为client k的本地的训练集个数；
            newWkt, nk = clientUpdate(k, wt)
            n += nk
            listWAndnk.append((newWkt, nk))
        # 4. 更新w值(加权平均)
        # Wt+1 <-- sum(Nk/n * Wt+1): 即n个clients的参数加权求和得出全局的Wt+1
        for k in range(len(listWAndnk)):
            wt = (listWAndnk[k][0]*listWAndnk[k][1])/n
    print("更新后的wt:", wt)
if __name__ == "__main__":
    server(0)