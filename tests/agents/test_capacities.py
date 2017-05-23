import os, sys, unittest
import numpy as np
import tensorflow as tf

dir = os.path.dirname(os.path.realpath(__file__))

from agents import capacities

class TestCapacities(unittest.TestCase):

    def test_eps_greedy(self):
        nb_state = 3
        nb_action = 2

        with tf.Graph().as_default():
            tf.set_random_seed(1)

            inputs = tf.random_uniform(shape=[2, 1], minval=0, maxval=3, dtype=tf.int32)
            # inputs = tf.Print(inputs, data=[inputs], message='inputs')

            Qs = tf.random_uniform(shape=[4, 3]) # 5 states, 3 actions per state
            # Qs = tf.Print(Qs, data=[Qs], message='Qs', summarize=12)

            q_preds = tf.squeeze(tf.nn.embedding_lookup(Qs, inputs), 1)
            # q_preds = tf.Print(q_preds, data=[q_preds], message='q_preds', summarize=6)

            actions = capacities.eps_greedy(inputs, q_preds, 2, 100, 0., 5)
            # actions = tf.Print(actions, data=[actions], message='actions')
# 
            with tf.Session() as sess:
                sess.run(tf.global_variables_initializer())

                inputs, actions = sess.run([inputs, actions])
                
                self.assertEqual(np.array_equal(inputs, [ [ 2 ], [ 1 ] ]), True)
                self.assertEqual(np.array_equal(actions, [ [ 1 ], [ 1 ] ]), True)

    def test_policy(self):
        policy_params = {
            'nb_inputs': 3
            , 'nb_units': 3
            , 'nb_outputs': 2
            , 'initial_mean': 0.
            , 'initial_stddev': .1
        }
        with tf.Graph().as_default():
            tf.set_random_seed(1)

            inputs = tf.placeholder(tf.float32, shape=[None, 3])
            probs_t, actions_t = capacities.policy(policy_params, inputs)

            with tf.Session() as sess:
                sess.run(tf.global_variables_initializer())

                probs, actions = sess.run([probs_t, actions_t], feed_dict={
                    inputs: [ [ -24, 10, 10 ]]
                })
                self.assertEqual(np.array_equal(np.round(probs, 1), [[ 0.5 , 0.5]]), True)
                self.assertEqual(np.array_equal(actions, [[0]]), True)

    def test_eligibilityTraces(self):
        with tf.Graph().as_default():
            inputs = tf.placeholder(tf.int32, shape=[])
            action_t = tf.placeholder(tf.int32, shape=[])
            shape = [3, 2]
            discount = .9
            lambda_value = .9

            et, update_et_op, reset_et_op = capacities.eligibilityTraces(inputs, action_t, shape, discount, lambda_value)

            with tf.Session() as sess:
                sess.run(tf.global_variables_initializer())

                _ = sess.run([update_et_op], feed_dict={
                    inputs: 0,
                    action_t: 1
                })
                self.assertEqual(np.array_equal(sess.run(et), [[ 0. , 1.], [ 0. , 0.], [ 0. , 0.]]), True)
                _ = sess.run([reset_et_op])
                self.assertEqual(np.array_equal(sess.run(et), [[ 0. , 0.], [ 0. , 0.], [ 0. , 0.]]), True)


if __name__ == "__main__":
    unittest.main()