#!/usr/bin/env python
# -*- coding: utf-8 -*-

# p58
# train dict{key=user: value=dict{key=itemID : value=操作类型，这里只关心点击与否所以恒为1}}
def ItemSimilarity( train ):
    # get co-rated users between items
    C = dict()   # Cij: 对物品i和j都感兴趣的用户数量
    N = dict()   # N[i] 对物品i感兴趣的用户数量
    for u, items in train.items():
        for i in items:
            N[i] += 1
            for j in items:
                if i == j:
                    continue
                C[i][j] += 1.0 / math.log(1.0 + len(items))

    # get final similarity matrix W
    W = dict()
    # related_items: 和物品i相似(有用户对他们都感兴趣)的物品集合
    for i, related_items in C.items():
        for j, cij in related_items.items():
            W[i][j] = cij / math.sqrt( N[i] * N[j] )

    return W


# p55
def Recommend( train, user, W, K ):
    rank = dict()
    interacted_items = train[user]
    for i, pi in interacted_items.items():
        # i: 指定user感兴趣的item; pi 操作类型恒为1
        # 前K个和物品i最相似的物
        for j, wij in sorted(W[i].items(), key=itemgetter(1), reverse=True)[0:K]:
            # j: 和i有相似度的item
            if j in interacted_items:  # 该物品已经是这个用户感兴趣的物品，跳过
                continue
            rank[j] += wij * pi
            #  rank[j].weight += wij * pi
            #  rank[j].reason[i] = wij * pi

    return rank
