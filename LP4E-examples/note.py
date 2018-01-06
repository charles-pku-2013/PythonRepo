#!! lambda for_each map function_object
    L = open( sys.argv[1] ).readlines()
    #    print L
    #!! 成员函数使用2种方法: 1. obj.func() 2. class.func(obj)
    #    L = map(str.strip, L)                   # 注意strip不带()
    #    L = map( lambda x: x.strip(), L )       #!! map with lambda
    #    L = [ (lambda x: x.strip()) for x in L ] #!! lambda只返回函数对象，要调用这个函数，必须与map结合
    #    L = [ x.strip() for x in L ]
    print L


# 查看版本号
print matplotlib.__version__

# 指定关键字排序
>>> S = 'spam'
>>> L = [1,2,3,4]
# Dict字典构造，用zip连接两个容器对应元素
>>> D = { k:v for (k,v) in zip(S, L) }
>>> print D
{'a': 3, 'p': 2, 's': 1, 'm': 4}
>>> I = D.items()
>>> print I
[('a', 3), ('p', 2), ('s', 1), ('m', 4)]
import operator
>>> I.sort( key=operator.itemgetter(1) )
>>> print I
[('s', 1), ('p', 2), ('a', 3), ('m', 4)]
>>> I.sort( key=operator.itemgetter(1), reverse=True )
>>> print I
[('m', 4), ('a', 3), ('p', 2), ('s', 1)]

#!! 复杂的复合类型字典
D = dict()
key = 'a'
D[key] = D.get(key, set())
S = D[key]
S.add(5)
D[key] = D.get(key, set())
S = D[key]
S.add(10)
print D


# 获取系统默认字符编码和文件系统字符编码
>>> import sys
>>> print sys.getdefaultencoding()
>>> print sys.getfilesystemencoding()
>>> print sys.stdin.encoding # 获取文件的字符编码
>>> print sys.stdout.encoding
# 设置系统默认字符编码
import sys
reload(sys) #!! python启动时候默认禁用sys.setdefaultencoding(),所以要reload解决问题
sys.setdefaultencoding('utf-8')

# main函数参数中有中文字符，要指定系统默认字符编码
import sys
reload(sys)
sys.setdefaultencoding('utf-8')     # 必须的
print sys.argv          # 显示字节内容
for S in sys.argv:
    print S.encode('utf-8') # 显示正确
# 测试 python test.py 中文参数

# main函数参数中有中文字符，指定解码
S = argv[1] # type(S) is str
U = S.decode('utf-8') # type(U) is unicode
print U # 可正常显示
T = S.decode( 'latin-1' ) # also unicode
# 创建unicode字符串
S = u'string'
# 判断字符串类型，ascii or unicode
isinstance( s, str )
isinstance( s, unicode )

# 列出中文文件名 for...in...
L = [ x.strip().decode('utf-8') for x in os.popen('ls') ]
# 直接print L 不能正常显示中文，应该：
for x in L:
    print x

# 执行含中文字符命令
L = [ x.strip().decode('utf-8') for x in os.popen("ls | grep \'测试\'") ]
# 命令字符串可以用unicode编码，但系统默认编码是ascii，须先设置reload(sys); sys.setdefaultencoding('utf-8')
L = [ x.strip().decode('utf-8') for x in os.popen(u"ls | grep \'测试\'") ]



#!! 关于字符集编码解码概念
# 编码 encode：将unicode字符串转换成为字节流str，能在网络上传输 序列化
S = u'中文' # 用系统编码生成一个unicode字符串
B = S.encode('utf-8') # 指定的编码可能不同于定义字符串时的系统默认编码。通过 locale -m 获知系统所支持的编码
type(S)         # <type 'unicode'>
type(B)         # <type 'str'>
for x in S:
...     print x
...
中
文
>>> B
'\xe4\xb8\xad\xe6\x96\x87'
>>> S
u'\u4e2d\u6587'
>>> print [ hex(ord(x)) for x in B ]
['0xe4', '0xb8', '0xad', '0xe6', '0x96', '0x87']
# 解码 decode: 将收到的str字节流转换成可识别的Unicode字符串 反序列化
# 如前文提到的将收到的main中文参数decode成unicode字符串, decode 指定的字符编码需要与encode所指定的一致
# Example
F = open( filename.encode('utf-8') )
# 若有 # -*- coding: utf-8 -*- 决定了str默认编码 可直接使用unicode字符串 无需encode

#!! 读取utf-8编码文件内容
L = codecs.open( sys.argv[1], 'r', encoding='utf-8' ).readlines()
# type(L[0]) 为 unicode
#!! 显示文件内容
for x in L:
    print x
#!! 不可以直接 print L 这样会输出unicode原始编码而不是翻译出来的实际字符


#!! 文件编码转换 file encoding converter
outFile = codecs.open(sys.argv[2], 'w', encoding='UTF-8')
for line in codecs.open(sys.argv[1], 'r', encoding='GB2312'):
    outFile.write( u'%s\n' % line.strip() )     #!! without CRLF line terminators
outFile.close()



# 自定义的类用作字典的key，需要重载__hash__和__eq__. hashcode 哈希 operator== 继承object
class MyThing(object):
    def __init__(self,name,location,length):
        self.name = name
        self.location = location
        self.length = length
    
    def __hash__(self):
        return hash((self.name, self.location))
    
    def __eq__(self, other):
        return (self.name, self.location) == (other.name, other.location)













