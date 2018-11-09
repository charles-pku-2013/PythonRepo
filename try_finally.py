#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://www.cnblogs.com/cotton/p/3785999.html

def func(x):
    try:
        return ++x
    finally:
        return x + 1

def f():
    try:
        print 1
        return 1
    finally:
        print 0
        return 0 # 去掉这个，执行try里的return
                 # try的返回值被finally的返回值覆盖了，或许是因为一个函数只能有一个返回值，以最后一个结果为准

if __name__ == '__main__':
    # x = 10
    # print func(x)
    # print 'x = %d' % x

    print 'f() = %d' % f()

"""
“如果try中没有异常，那么except部分将跳过，执行else中的语句。
finally是无论是否有异常，最后都要做的一些事情。”
这里补充一句，在含有return的情况下，并不会阻碍finally的执行。
"""
