import numpy as np
import tensorflow as tf

# All those capacities will be applied in the current default graph
# Use it this way:
# with my_graph.as_default():
#     my_capacity()

def epsGreedy(inputs_t, q_preds_t, nb_actions, N0, min_eps, nb_state=None):
    with tf.variable_scope('EpsilonGreedyPolicy'):
        N0_t = tf.constant(N0, tf.float32, name='N0')
        min_eps_t = tf.constant(min_eps, tf.float32, name='min_eps')

        if nb_state == None:
            N = tf.Variable(0., trainable=False, dtype=tf.float32, name='N')
            update_N = tf.assign(N, N + 1)
            eps = tf.maximum(N0_t / (N0_t + N), min_eps_t, name="eps")
        else:
            N = tf.Variable(tf.ones(shape=[nb_state]), name='N', trainable=False)
            update_N = tf.scatter_add(N, inputs_t, 1)
            eps = tf.maximum(N0_t / (N0_t + N[inputs_t]), min_eps_t, name="eps")
        cond = tf.greater(tf.random_uniform([], 0, 1), eps)
        pred_action = tf.cast(tf.argmax(q_preds_t, 0), tf.int32)
        random_action = tf.random_uniform([], 0, nb_actions, dtype=tf.int32)
        with tf.control_dependencies([update_N]):
            action_t = tf.cond(cond, lambda: pred_action, lambda: random_action)

    return action_t

def tabularQValue(nb_state, nb_action):    
    scope = tf.VariableScope('TabularQValue')
    with tf.variable_scope(scope, reuse=False):
        Q = tf.get_variable(
            'Q'
            , shape=[nb_state, nb_action]
            , initializer=tf.zeros_initializer()
            , dtype=tf.float32
        )

    def apply(inputs_t):
        with tf.variable_scope(scope, reuse=True):
            Q = tf.get_variable('Q')
            out = tf.nn.embedding_lookup(Q, inputs_t)

        return out
        
    return apply


def MSETabularQLearning(Qs_t, discount, q_preds, action_t, optimizer=None):
    with tf.variable_scope('MSEQLearning'):
        q_t = q_preds[action_t]
        reward = tf.placeholder(tf.float32, shape=[], name="reward")
        next_state = tf.placeholder(tf.int32, shape=[], name="nextState")
        next_max_action_t = tf.cast(tf.argmax(Qs_t[next_state], 0), tf.int32)
        target_q = tf.stop_gradient(reward + discount * Qs_t[next_state, next_max_action_t], name='target_q')
        loss = 1/2 * tf.square(target_q - q_t)

        global_step = tf.Variable(0, trainable=False, name="global_step", collections=[tf.GraphKeys.GLOBAL_STEP, tf.GraphKeys.GLOBAL_VARIABLES])
        if optimizer == None:
            learning_rate = tf.train.inverse_time_decay(1., global_step, 1, 0.001, staircase=False, name="decay_lr")
            optimizer = tf.train.GradientDescentOptimizer(learning_rate)
        train_op = optimizer.minimize(loss, global_step=global_step)

    return (reward, next_state, loss, train_op)

def counter():
    count_t = tf.Variable(0, trainable=False)
    inc_count_op = tf.assign(count_t, count_t + 1)

    return (count_t, inc_count_op)

