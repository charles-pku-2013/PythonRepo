#!/usr/bin/jython
# -*- coding:utf8

import tensorflow as tf

module = tf.load_op_library('./zero_out.so')


with tf.Session() as sess:
    #  sess.run(tf.global_variables_initializer())
    input = tf.placeholder(tf.int32, name='input')
    op = module.zero_out
    #  print type(op)
    output = op(input)
    print sess.run(output, feed_dict={input : [5,4,3,2,1]})

    print 'exporting graph...'
    #  tf.train.write_graph(sess.graph, '.', 'saved_model.pb', as_text=False)
    builder = tf.saved_model.builder.SavedModelBuilder("./zero_out")

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
