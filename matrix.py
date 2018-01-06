#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from numpy import *

matrix1 = None
matrix2 = None


def writeToFile( matrix, filename ):
    (m,n) = shape(matrix)
    F = open(filename, 'w')
    for i in range(m):
        for j in range(n):
            F.write('%s ' % int(matrix[i,j]))
        F.write('\n')


def generate_matrix( m1row, m1col, m2row, m2col, maxVal ):
    global matrix1
    global matrix2
    matrix1 = random.randint( 0, maxVal, (m1row, m1col) )   #!! 生成指定维度的整数矩阵
    matrix2 = random.randint( 0, maxVal, (m2row, m2col) )
#    matrix1 = random.rand( m1row, m1col )
#    matrix2 = random.rand( m2row, m2col )
#    for i in range(m1row):
#        for j in range(m1col):
#            matrix1[i,j] = int(str(matrix1[i,j]).split('.')[1]) % maxVal
#    for i in range(m2row):
#        for j in range(m2col):
#            matrix2[i,j] = int(str(matrix2[i,j]).split('.')[1]) % maxVal
    matrix1 = mat(matrix1)
    matrix2 = mat(matrix2)



if __name__ == '__main__':
    m1row = int( sys.argv[1] )
    m1col = int( sys.argv[2] )
    m2row = int( sys.argv[3] )
    m2col = int( sys.argv[4] )
    maxVal = int( sys.argv[5] )

    generate_matrix( m1row, m1col, m2row, m2col, maxVal )

#    print matrix1
#    print matrix2
#    print type(matrix1)
#    print type(matrix2)

    result = matrix1 * matrix2
    
#    print result
#    print type( matrix1[0,0] )
#    print int( matrix1[0,0] )

    writeToFile( matrix1, 'm1.txt' )
    writeToFile( matrix2, 'm2.txt' )
    writeToFile( result, 'result.txt' )








