#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MacOS下测试通过

测试步骤：
1. Install pre-built tensorflow
        pip install tensorflow
2. Install pre-built boost C++ library
        brew install boost
3. run ./compile.sh and get tokenizer.so
4. run this python script

"""

import tensorflow as tf

module = tf.load_op_library('./tokenizer.so')

class TokenizerTest(tf.test.TestCase):
    def testTokenize(self):
        with self.test_session():
            op = module.tokenize
            result = op('')
            self.assertAllEqual(result.eval(), [])
            result = op([])
            self.assertAllEqual(result.eval(), [])
            result = op('六年后，他来到莲花山脚下的深圳改革开放展览馆，参观“大潮起珠江——广东改革开放40周年展览”。')
            self.assertAllEqual(result.eval(), ['六','年','后','他','来','到','莲','花','山','脚','下','的','深','圳','改','革','开','放','展','览','馆','参','观','大','潮','起','珠','江','广','东','改','革','开','放','40#','#40','周','年','展','览'])
            result = op(['京东商城','京东到家','京东配送'])
            self.assertAllEqual(result.eval(), ['京','东','商','城']) # NOTE tokenize暂一次只处理一个字符串
            # print result.eval()
            # for item in result.eval():
                # print item.decode('utf-8')
        print 'testTokenize pass'

    def testGetBigrams(self):
        with self.test_session():
            op = module.get_bigrams
            result = op([])
            self.assertAllEqual(result.eval(), [])
            result = op([''])
            self.assertAllEqual(result.eval(), ['^ ',' $']) # TODO 空字符串返回格式是否符合预期
            result = op(['北京','上海','重庆','武汉','香港','台北'])
            self.assertAllEqual(result.eval(), ['^ 北京','北京 上海','上海 重庆','重庆 武汉','武汉 香港','香港 台北','台北 $'])
            result = op(['北京'])
            self.assertAllEqual(result.eval(), ['^ 北京','北京 $'])
            # print result.eval()
            # for item in result.eval():
                # print item.decode('utf-8')
        print 'testGetBigrams pass'

    def testGetUnigramsAndBigrams(self):
        with self.test_session():
            op = module.get_unigrams_and_bigrams
            result = op([])
            self.assertAllEqual(result.eval(), [])
            result = op([''])
            self.assertAllEqual(result.eval(), [])
            result = op(['相关性'])
            self.assertAllEqual(result.eval(), ['相','关','性','^ 相','相 关','关 性','性 $'])
            # print result.eval()
            # for item in result.eval():
                # print item.decode('utf-8')
        print 'testGetUnigramsAndBigrams pass'

if __name__ == "__main__":
    tf.test.main()
