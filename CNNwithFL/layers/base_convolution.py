# _*_ coding:utf-8 _*_
import numpy as np
from functools import reduce
import math


class Conv2D(object):
    # [batch_size, 28, 28, 1], 12, 5, 1, "VALID", wt
    def __init__(self, shape, output_channels, ksize=3, stride=1, method='VALID', wt=0, isFirstConv = 2):
        '''
        输入数据的shape, filter的个数，filter的尺寸， 步长， 是否通过padding输出原尺寸大小, wt 模型参数， isFirstConv是否第二层参数,默认取二
        '''
        self.input_shape = shape # [batch_size, 28, 28, 1]
        self.output_channels = output_channels
        self.input_channels = shape[-1]
        self.batchsize = shape[0]
        self.stride = stride
        self.ksize = ksize
        self.method = method
        self.wt = wt
        self.isFirstConv = isFirstConv
        # 设置参数初始化，进行normalization, 加速收敛
        weights_scale = math.sqrt(reduce(lambda x, y: x * y, shape) / self.output_channels)
        self.weights = np.random.standard_normal(
            (ksize, ksize, self.input_channels, self.output_channels)) / weights_scale
        self.bias = np.random.standard_normal(self.output_channels) / weights_scale
        # TODO(fallenkliu@gmail.com): if global train times > 1 change weights and bias
        # 判断传入参数 非0则表示 修改第一层的参数
        if wt != 0 and self.isFirstConv == 1:
            self.weights = wt[0]
            self.bias = wt[1]

        if method == 'VALID':
            self.eta = np.zeros((shape[0], int((shape[1] - ksize + 1) / self.stride), int((shape[1] - ksize + 1) / self.stride),
             self.output_channels))

        if method == 'SAME':
            self.eta = np.zeros((shape[0], shape[1]//self.stride, shape[2]//self.stride,self.output_channels))

        self.w_gradient = np.zeros(self.weights.shape)
        self.b_gradient = np.zeros(self.bias.shape)
        self.output_shape = self.eta.shape

        if (shape[1] - ksize) % stride != 0:
            print('input tensor width can\'t fit stride')
        if (shape[2] - ksize) % stride != 0:
            print('input tensor height can\'t fit stride')

    def forward(self, x):
        col_weights = self.weights.reshape([-1, self.output_channels])
        if self.method == 'SAME':
            x = np.pad(x, (
                (0, 0), (self.ksize / 2, self.ksize / 2), (self.ksize / 2, self.ksize / 2), (0, 0)),
                             'constant', constant_values=0)

        self.col_image = []
        conv_out = np.zeros(self.eta.shape)
        for i in range(self.batchsize):
            img_i = x[i][np.newaxis, :]
            self.col_image_i = im2col(img_i, self.ksize, self.stride)
            conv_out[i] = np.reshape(np.dot(self.col_image_i, col_weights) + self.bias, self.eta[0].shape)
            self.col_image.append(self.col_image_i)

        self.col_image = np.array(self.col_image)
        return conv_out

    def gradient(self, eta):
        self.eta = eta
        col_eta = np.reshape(eta, [self.batchsize, -1, self.output_channels])

        for i in range(self.batchsize):
            self.w_gradient += np.dot(self.col_image[i].T, col_eta[i]).reshape(self.weights.shape)
        self.b_gradient += np.sum(col_eta, axis=(0, 1))

        # deconv of padded eta with flippd kernel to get next_eta
        if self.method == 'VALID':
            pad_eta = np.pad(self.eta, (
                (0, 0), (self.ksize - 1, self.ksize - 1), (self.ksize - 1, self.ksize - 1), (0, 0)),
                             'constant', constant_values=0)

        if self.method == 'SAME':
            pad_eta = np.pad(self.eta, (
                (0, 0), (self.ksize / 2, self.ksize / 2), (self.ksize / 2, self.ksize / 2), (0, 0)),
                             'constant', constant_values=0)

        col_pad_eta = np.array([im2col(pad_eta[i][np.newaxis, :], self.ksize, self.stride) for i in range(self.batchsize)])
        flip_weights = np.flipud(np.fliplr(self.weights))
        col_flip_weights = flip_weights.reshape([-1, self.input_channels])
        next_eta = np.dot(col_pad_eta, col_flip_weights)
        next_eta = np.reshape(next_eta, self.input_shape)
        return next_eta

    def backward(self, alpha=0.00001, weight_decay=0.0004):
        # weight_decay = L2 regularization
        self.weights *= (1 - weight_decay)
        self.bias *= (1 - weight_decay)
        self.weights -= alpha * self.w_gradient
        self.bias -= alpha * self.bias

        self.w_gradient = np.zeros(self.weights.shape)
        self.b_gradient = np.zeros(self.bias.shape)


# def im2col(image, ksize, stride):
#     # image is a 4d tensor([batchsize, width ,height, channel])
#     img = []
#     for b in range(image.shape[0]):
#         per_image_col = []
#         for i in range(0, image.shape[1] - ksize + 1, stride):
#             for j in range(0, image.shape[2] - ksize + 1, stride):
#                 col = image[0, i:i + ksize, j:j + ksize, :].reshape([-1])
#                 per_image_col.append(col)
#         per_image_col = np.array(per_image_col)
#         img.append(per_image_col)
#     return np.array(img)

def im2col(image, ksize, stride):
    # image is a 4d tensor([batchsize, width ,height, channel])
    image_col = []
    for i in range(0, image.shape[1] - ksize + 1, stride):
        for j in range(0, image.shape[2] - ksize + 1, stride):
            col = image[:, i:i + ksize, j:j + ksize, :].reshape([-1])
            image_col.append(col)
    image_col = np.array(image_col)

    return image_col


if __name__ == "__main__":
    # img = np.random.standard_normal((2, 32, 32, 3))
    img = np.ones((1, 32, 32, 3))
    img *= 2
    conv = Conv2D(img.shape, 12, 3, 1)
    next = conv.forward(img)
    next1 = next.copy() + 1
    conv.gradient(next1-next)
    print(conv.w_gradient)
    print(conv.b_gradient)
    conv.backward()
