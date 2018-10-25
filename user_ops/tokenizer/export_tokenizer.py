#!/usr/bin/jython
# -*- coding:utf8

import tensorflow as tf

module = tf.load_op_library('./tokenizer.so')


with tf.Session() as sess:
    #  sess.run(tf.global_variables_initializer())
    input = tf.placeholder(tf.string, name='input')
    op = module.get_bigrams
    # op = module.get_unigrams_and_bigrams
    # print type(op)
    output = op(input)
    # outArr = sess.run(output, feed_dict={input : [""]})
    # outArr = sess.run(output, feed_dict={input : [""]})
    # outArr = sess.run(output, feed_dict={input : ["北京"]})
    outArr = sess.run(output, feed_dict={input : ["北京","上海","天津","重庆","深圳","香港"]})
    # outArr = sess.run(output, feed_dict={input : ["水写布", "仿宣纸"]}) # get_bigrams
    # outArr = sess.run(output, feed_dict={input : ["相关性"]}) # get_unigrams_and_bigrams

    for str in outArr:
        print str.decode('utf-8')

    print 'exporting graph...'
    #  tf.train.write_graph(sess.graph, '.', 'saved_model.pb', as_text=False)
    builder = tf.saved_model.builder.SavedModelBuilder("./tokenizer")

    signature = (
      tf.saved_model.signature_def_utils.build_signature_def(
          inputs={
              tf.saved_model.signature_constants.PREDICT_INPUTS:
                  tf.saved_model.utils.build_tensor_info(input)
          },
          outputs={
              tf.saved_model.signature_constants.PREDICT_OUTPUTS:
                  tf.saved_model.utils.build_tensor_info(output)
          },
          method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))

    builder.add_meta_graph_and_variables(
          sess, [tf.saved_model.tag_constants.SERVING],
          signature_def_map={
              tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                  signature,
          },
          main_op=tf.tables_initializer(),
          strip_default_attrs=True)
    builder.save()
