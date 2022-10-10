#!/usr/bin/env python3.7.9
"""
Copyright © 2021 DUE TUL
@ desc  : This modules is used to load raw data
@ author: BOHAO CHU
"""
import os

import numpy

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import arguments as arg
import reader
import tensorflow as tf
from tensorflow import keras

'''
physical_devices = tf.config.list_physical_devices("GPU")
tf.config.experimental.set_memory_growth(physical_devices[0], True)
'''

# cnn model
class SensorCNN(keras.Model):
    def __init__(self):
        super(SensorCNN, self).__init__()
        self.conv1 = keras.layers.Conv2D(filters=32, kernel_size=3, padding='same', activation=tf.nn.relu)
        self.pool1 = keras.layers.MaxPool2D(pool_size=2, strides=2)
        self.conv2 = keras.layers.Conv2D(filters=64, kernel_size=3, padding='same', activation=tf.nn.relu)
        self.pool2 = keras.layers.MaxPool2D(pool_size=2, strides=2)
        self.flatten = keras.layers.Flatten()
        self.dense1 = keras.layers.Dense(units=128, activation=tf.nn.tanh)
        self.dense2 = keras.layers.Dense(units=1, activation=tf.nn.sigmoid)

    def call(self, input_tensor):
        x = self.conv1(input_tensor)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.flatten(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return x


# mlp model
class SensorMLP(keras.Model):
    def __init__(self):
        super(SensorMLP, self).__init__()
        self.flatten = keras.layers.Flatten()
        self.hidden1 = keras.layers.Dense(units=10, activation=tf.nn.relu)
        self.hidden2 = keras.layers.Dense(units=1, activation=tf.nn.sigmoid)

    def call(self, input_tensor):
        x = self.flatten(input_tensor)
        x = self.hidden1(x)
        x = self.hidden2(x)
        return x


# main function
if __name__ == "__main__":
    print(tf.__version__)
    # load train and test data
    train_dataset = reader.train_reader_tfrecord(
        data_path=arg.train_path,
        num_epochs=arg.NUM_EPOCHS,
        batch_size=arg.BATCH_SIZE)
    test_dataset = reader.test_reader_tfrecord(
        data_path=arg.test_path)

    # init models
    mic_model = SensorCNN()
    acc_x_model = SensorCNN()
    acc_y_model = SensorCNN()
    acc_z_model = SensorCNN()
    laser_model = SensorMLP()

    # init optimizers
    mic_optimizer = keras.optimizers.SGD(learning_rate=1e-2)
    acc_x_optimizer = keras.optimizers.SGD(learning_rate=1e-2)
    acc_y_optimizer = keras.optimizers.SGD(learning_rate=1e-2)
    acc_z_optimizer = keras.optimizers.SGD(learning_rate=1e-2)
    laser_optimizer = keras.optimizers.SGD(learning_rate=1e-1)

    # init loss functions
    loss_function = keras.losses.BinaryCrossentropy(from_logits=True)

    # init metrics
    metric = keras.metrics.BinaryAccuracy()

    # train model
    for epoch in range(100):
        print(f"\nStart of Training Epoch {epoch} of {arg.activity}")
        # init losses
        mic_losses = []
        acc_x_losses = []
        acc_y_losses = []
        acc_z_losses = []
        laser_losses = []

        # init accuracy
        mic_accuracy = []
        acc_x_accuracy = []
        acc_y_accuracy = []
        acc_z_accuracy = []
        laser_accuracy = []

        for batch_idx, data_batch in enumerate(train_dataset):
            # Load merger feature
            x_batch = data_batch['data'].numpy().reshape((-1, arg.feature_row, arg.feature_column, 1))
            y_batch = data_batch['label'].numpy().reshape((-1, 1))

            # split merger feature for single model
            mic_input = x_batch[:, :, 0:arg.mic_end, :]
            acc_x_input = x_batch[:, :, arg.mic_end:arg.acc_x_end, :]
            acc_y_input = x_batch[:, :, arg.acc_x_end:arg.acc_y_end, :]
            acc_z_input = x_batch[:, :, arg.acc_y_end:arg.acc_z_end, :]
            laser_input = x_batch[:, :, arg.acc_z_end:arg.laser_end, :]

            # update gradients
            with tf.GradientTape() as tape:
                mic_out = mic_model(mic_input)
                mic_loss = loss_function(y_batch, mic_out)
                mic_gradients = tape.gradient(mic_loss, mic_model.trainable_variables)
                mic_optimizer.apply_gradients(zip(mic_gradients, mic_model.trainable_variables))
            mic_losses.append(mic_loss)
            metric.update_state(y_batch, mic_out)
            mic_accuracy.append(metric.result())
            metric.reset_states()

            with tf.GradientTape() as tape:
                acc_x_out = acc_x_model(acc_x_input)
                acc_x_loss = loss_function(y_batch, acc_x_out)
                acc_x_gradients = tape.gradient(acc_x_loss, acc_x_model.trainable_variables)
                acc_x_optimizer.apply_gradients(zip(acc_x_gradients, acc_x_model.trainable_variables))
            acc_x_losses.append(acc_x_loss)
            metric.update_state(y_batch, acc_x_out)
            acc_x_accuracy.append(metric.result())
            metric.reset_states()

            with tf.GradientTape() as tape:
                acc_y_out = acc_y_model(acc_y_input)
                acc_y_loss = loss_function(y_batch, acc_y_out)
                acc_y_gradients = tape.gradient(acc_y_loss, acc_y_model.trainable_variables)
                acc_y_optimizer.apply_gradients(zip(acc_y_gradients, acc_y_model.trainable_variables))
            acc_y_losses.append(acc_y_loss)
            metric.update_state(y_batch, acc_y_out)
            acc_y_accuracy.append(metric.result())
            metric.reset_states()

            with tf.GradientTape() as tape:
                acc_z_out = acc_z_model(acc_z_input)
                acc_z_loss = loss_function(y_batch, acc_z_out)
                acc_z_gradients = tape.gradient(acc_z_loss, acc_z_model.trainable_variables)
                acc_z_optimizer.apply_gradients(zip(acc_z_gradients, acc_z_model.trainable_variables))
            acc_z_losses.append(acc_z_loss)
            metric.update_state(y_batch, acc_z_out)
            acc_z_accuracy.append(metric.result())
            metric.reset_states()

            with tf.GradientTape() as tape:
                laser_out = laser_model(laser_input)
                laser_loss = loss_function(y_batch, laser_out)
                laser_gradients = tape.gradient(laser_loss, laser_model.trainable_variables)
                laser_optimizer.apply_gradients(zip(laser_gradients, laser_model.trainable_variables))
            laser_losses.append(laser_loss)
            metric.update_state(y_batch, laser_out)
            laser_accuracy.append(metric.result())
            metric.reset_states()

        print("Over Train Dataset")
        print(f"mic accuracy  : {numpy.sum(mic_accuracy) / len(mic_accuracy)}, "
              f"loss:{numpy.sum(mic_losses) / len(mic_losses)}")
        print(f"acc_x accuracy: {numpy.sum(acc_x_accuracy) / len(acc_x_accuracy)}, "
              f"loss:{numpy.sum(acc_x_losses) / len(acc_x_losses)}")
        print(f"acc_y accuracy: {numpy.sum(acc_y_accuracy) / len(acc_y_accuracy)}, "
              f"loss:{numpy.sum(acc_y_losses) / len(acc_y_losses)}")
        print(f"acc_z accuracy: {numpy.sum(acc_z_accuracy) / len(acc_z_accuracy)}, "
              f"loss:{numpy.sum(acc_z_losses) / len(acc_z_losses)}")
        print(f"laser accuracy: {numpy.sum(laser_accuracy) / len(laser_accuracy)}, "
              f"loss:{numpy.sum(laser_losses) / len(laser_losses)}")

        # init losses
        mic_losses = []
        acc_x_losses = []
        acc_y_losses = []
        acc_z_losses = []
        laser_losses = []

        # init accuracy
        mic_accuracy = []
        acc_x_accuracy = []
        acc_y_accuracy = []
        acc_z_accuracy = []
        laser_accuracy = []
        for batch_idx, data_batch in enumerate(test_dataset):
            # Load merger feature
            x_batch = data_batch['' \
                                 'data'].numpy().reshape((-1, arg.feature_row, arg.feature_column, 1))
            y_batch = data_batch['label'].numpy().reshape((-1, 1))

            # split merger feature for single model
            mic_input = x_batch[:, :, 0:arg.mic_end, :]
            acc_x_input = x_batch[:, :, arg.mic_end:arg.acc_x_end, :]
            acc_y_input = x_batch[:, :, arg.acc_x_end:arg.acc_y_end, :]
            acc_z_input = x_batch[:, :, arg.acc_y_end:arg.acc_z_end, :]
            laser_input = x_batch[:, :, arg.acc_z_end:arg.laser_end, :]

            # update gradients
            mic_out = mic_model(mic_input)
            mic_loss = loss_function(y_batch, mic_out)
            mic_losses.append(mic_loss)
            metric.update_state(y_batch, mic_out)
            mic_accuracy.append(metric.result())
            metric.reset_states()

            acc_x_out = acc_x_model(acc_x_input)
            acc_x_loss = loss_function(y_batch, acc_x_out)
            acc_x_losses.append(acc_x_loss)
            metric.update_state(y_batch, acc_x_out)
            acc_x_accuracy.append(metric.result())
            metric.reset_states()

            acc_y_out = acc_y_model(acc_y_input)
            acc_y_loss = loss_function(y_batch, acc_y_out)
            acc_y_losses.append(acc_y_loss)
            metric.update_state(y_batch, acc_y_out)
            acc_y_accuracy.append(metric.result())
            metric.reset_states()

            acc_z_out = acc_z_model(acc_z_input)
            acc_z_loss = loss_function(y_batch, acc_z_out)
            acc_z_losses.append(acc_z_loss)
            metric.update_state(y_batch, acc_z_out)
            acc_z_accuracy.append(metric.result())
            metric.reset_states()

            laser_out = laser_model(laser_input)
            laser_loss = loss_function(y_batch, laser_out)
            laser_losses.append(laser_loss)
            metric.update_state(y_batch, laser_out)
            laser_accuracy.append(metric.result())
            metric.reset_states()

        print("Over Test Dataset")
        print(f"mic accuracy  : {numpy.sum(mic_accuracy) / len(mic_accuracy)}, "
              f"loss:{numpy.sum(mic_losses) / len(mic_losses)}")
        print(f"acc_x accuracy: {numpy.sum(acc_x_accuracy) / len(acc_x_accuracy)}, "
              f"loss:{numpy.sum(acc_x_losses) / len(acc_x_losses)}")
        print(f"acc_y accuracy: {numpy.sum(acc_y_accuracy) / len(acc_y_accuracy)}, "
              f"loss:{numpy.sum(acc_y_losses) / len(acc_y_losses)}")
        print(f"acc_z accuracy: {numpy.sum(acc_z_accuracy) / len(acc_z_accuracy)}, "
              f"loss:{numpy.sum(acc_z_losses) / len(acc_z_losses)}")
        print(f"laser accuracy: {numpy.sum(laser_accuracy) / len(laser_accuracy)}, "
              f"loss:{numpy.sum(laser_losses) / len(laser_losses)}")

        tf.saved_model.save(mic_model, f"{arg.tensorflow_model_path}/mic")
        tf.saved_model.save(acc_x_model, f"{arg.tensorflow_model_path}/acc_x")
        tf.saved_model.save(acc_y_model, f"{arg.tensorflow_model_path}/acc_y")
        tf.saved_model.save(acc_z_model, f"{arg.tensorflow_model_path}/acc_z")
        tf.saved_model.save(laser_model, f"{arg.tensorflow_model_path}/laser")
