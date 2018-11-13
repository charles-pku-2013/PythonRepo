#!/usr/bin/env python
# -*- coding: utf-8 -*-

dict = {}
dict['key'] = []
dict['key'].append(1)
print dict

# val是指向dict['key']的引用,更像指针
val = dict['key']
val.append(2)
val.append(3)
print dict

another_list = [10, 20, 30]
# NOTE val现在指向another_list的引用，不再指向dict['key']
val = another_list
print dict

