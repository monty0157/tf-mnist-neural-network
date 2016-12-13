import tensorflow as tf
import layers
import parameters

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

batch_size = 100
learning_rate = 10
training_epochs = 10
parameter_value_manual = 2
parameter_list = []
activated_units = []

with tf.name_scope('output'):
    y_output = tf.placeholder(tf.float32, shape=(None, 10), name="y-output")


def neural_network(data, n_nodes_layers = None, n_hidden_layers = None):

    if n_nodes_layers is None:
        n_nodes_layers = [n_nodes_layer_input, n_nodes_layer_output]

    if len(n_nodes_layers) != (n_hidden_layers + 2):
        raise ValueError('Number of hidden layers does not match layers in the list n_nodes_layers')


    for n in range(n_hidden_layers+1):
        parameters_n = parameters.layer(n_nodes_layers[n], n_nodes_layers[n+1])
        parameter_list.append(parameters_n)


    parameters_output = parameters.layer(n_nodes_layers[-2], n_nodes_layers[-1])


    if n_hidden_layers is None:
        output = layers.hidden(data, parameters_output)
    else:
        activated_units.append(data)
        for i in range(len(parameter_list)):
            z_hl = layers.hidden_layer(activated_units[i], parameter_list[i])
            activated_units.append(z_hl)

        output = layers.hidden_layer(activated_units[len(activated_units)-2], parameters_output)

    return output

def train_neural_network(x, n_nodes_layers, n_hidden_layers):
    prediction = neural_network(x, n_nodes_layers, n_hidden_layers)
    with tf.name_scope("cost"):
        #cost = tf.contrib.losses.mean_squared_error(prediction, y_output)
        cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(prediction, y_output))
        optimizer = tf.train.GradientDescentOptimizer(learning_rate, name='GradientDescent').minimize(cost)
        tf.summary.scalar("cost", cost)

    correct = tf.equal(tf.argmax(prediction, 1), tf.argmax(y_output, 1))


    with tf.name_scope('accuracy'):
       accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
       tf.summary.scalar("accuracy", accuracy)


    with tf.Session() as sess:
        summary_op = tf.merge_all_summaries()
        writer = tf.train.SummaryWriter("./logs/300units", graph=tf.get_default_graph())

        sess.run(tf.global_variables_initializer())

        for epoch in range(training_epochs):
            epoch_loss = 0
            for j in range(int(mnist.train.num_examples/batch_size)):
                epoch_x, epoch_y = mnist.train.next_batch(batch_size)
                j, c, summary = sess.run([optimizer, cost, summary_op], feed_dict = {x: epoch_x, y_output: epoch_y })
                epoch_loss += c

                writer.add_summary(summary, j)

            print('Epoch', epoch, 'completed out of', training_epochs, 'loss:', epoch_loss,)


        print('Accuracy:', accuracy.eval({x:mnist.test.images, y_output:mnist.test.labels}))
