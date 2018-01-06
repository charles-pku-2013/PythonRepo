from numpy import *

# 4x4 随机二维数组 ndarray 再转矩阵 mat
array = random.rand(4, 4)
matrix = mat(array)     # mat matrix 至少2维
# 矩阵求逆 逆矩阵
invMatrix = matrix.I
# 转置矩阵
matrix.T
# 单位矩阵
Eye = eye(4)

# array和mat区别, array不能转置，求逆，可由array构造mat
# mat下标访问方式 m[i,j]
# 获取mat维度shape(m)




