#!/usr/bin/env python
# -*- coding: utf-8 -*-

# W[][] 是嵌套的dict

# 最笨的办法
# train dict{key=user: value=dict{key=itemID : value=操作类型，这里只关心点击与否所以恒为1}}
# {user : {item : item_attr}}
def UserSimilarity1( train ):
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue
            W[u][v] = len( train[u] & train[v] )
            W[u][v] /= math.sqrt( len(train[u]) * len(train[v]) )
    return W


# p49
def UserSimilarity2( train ):
    # 首先建立从物品到用户的倒排表
    item_users = dict()   # dict{key = item, value = set(users)}
    # train.items() dict类型成员函数，返回key,value pair list
    for u, items in train.items():
        for i in items.keys():  # 对于用户u兴趣列表中的每一个item
            if i not in item_users: # 表中还没有 item_i 的记录
                item_users[i] = set() # 建立该表项
            item_users[i].add(u)

    # 得到用户共同感兴趣的物品 co-rated items between users
    C = dict()  # 用户间相似度计数, 对称矩阵
    N = dict()  # 用户u的兴趣列表长度
    for i, users in item_users.items():
        for u in users:
            N[u] += 1
            # 这里重复计算了，只需要计算上三角就行
            for v in users:
                if u == v:
                    continue
                C[u][v] += 1 / math.log(1 + len(users)) # 用户u,v兴趣列表交集的长度

    # get final similarity matrix W
    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():  # cuv is C[u][v]
            W[u][v] = cuv / math.sqrt( N(u) * N(v) )

    return W


# W 用户兴趣相似度矩阵 W = dict{key=user : value=dict{key=userV : value=wuv_similarity}}
# W[user] = dict{key=userV : value=wuv}
# train = dict{key=user : value=itemset} 用户交互过的物品集合
# 目标：给用户user推荐与他兴趣最相似的k个用户喜欢的物品
"""
UserCF算法：先找出与用户user兴趣相似度最近的k个用户，用v遍历
对于用户v所感兴趣的物品，查看其是否也是user所感兴趣的，
若是，跳过；不是，则设置推荐系数 += wuv
"""
def Recommend( user, train, W, K )
    rank = dict()  # rank = dict{item : 推荐度}
    interacted_items = train[user]
    # 取用户user前k个相似度最大的, itemgetter(1) 第二个关键字, 即wuv
    # v W矩阵的列下标: 用户
    # 找与用户user兴趣最相似的k个用户，用v遍历
    for v, wuv in sorted(W[user].items, key=itemgetter(1), reverse=True)[0:K]:
        for i, rvi in train[v].items():  # 用户v的兴趣物品列表, rvi恒为1 p47
            if i in interacted_items[v].items():
                # filter items user interacted before
                continue
            rank[i] += wuv * rvi

    return rank
