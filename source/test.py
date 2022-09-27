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

physical_devices = tf.config.list_physical_devices("GPU")
tf.config.experimental.set_memory_growth(physical_devices[0], True)



# mlp model
class FinalMLP(keras.Model):
    def __init__(self):
        super(FinalMLP, self).__init__()
        self.hidden = keras.layers.Dense(units=1, activation=tf.nn.sigmoid)

    def call(self, input_tensor):
        x = self.hidden(input_tensor)
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

    # load single models
    mic_model = tf.saved_model.load(f"models/tensorflow/{arg.database}/{arg.activity}/mic")
    acc_x_model = tf.saved_model.load(f"models/tensorflow/{arg.database}/{arg.activity}/acc_x")
    acc_y_model = tf.saved_model.load(f"models/tensorflow/{arg.database}/{arg.activity}/acc_y")
    acc_z_model = tf.saved_model.load(f"models/tensorflow/{arg.database}/{arg.activity}/acc_z")
    laser_model = tf.saved_model.load(f"models/tensorflow/{arg.database}/{arg.activity}/laser")

    # init final model
    final_model = FinalMLP()

    # init optimizers
    final_optimizer = keras.optimizers.SGD(learning_rate=1e-2)
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
        final_losses = []

        # init accuracy
        mic_accuracy = []
        acc_x_accuracy = []
        acc_y_accuracy = []
        acc_z_accuracy = []
        laser_accuracy = []
        final_accuracy = []

        for batch_idx, data_batch in enumerate(train_dataset):
            # Load merger feature
            x_batch = data_batch['data'].numpy().reshape((-1, arg.feature_row, arg.feature_column, 1))
            y_batch = data_batch['label'].numpy().reshape((-1, 1))

            # split merger feature for single models
            mic_input = x_batch[:, :, 0:arg.mic_end, :]
            acc_x_input = x_batch[:, :, arg.mic_end:arg.acc_x_end, :]
            acc_y_input = x_batch[:, :, arg.acc_x_end:arg.acc_y_end, :]
            acc_z_input = x_batch[:, :, arg.acc_y_end:arg.acc_z_end, :]
            laser_input = x_batch[:, :, arg.acc_z_end:arg.laser_end, :]

            # predicted result of single models
            mic_out = mic_model(mic_input)
            acc_x_out = acc_x_model(acc_x_input)
            acc_y_out = acc_y_model(acc_y_input)
            acc_z_out = acc_z_model(acc_z_input)
            laser_out = laser_model(laser_input)

            # concat the output of single models as the input of final model
            final_input = tf.concat([mic_out, acc_x_out, acc_y_out, acc_z_out, laser_out], 1)

            # update gradients
            with tf.GradientTape() as tape:
                final_out = final_model(final_input)
                final_loss = loss_function(y_batch, final_out)
                final_gradients = tape.gradient(final_loss, final_model.trainable_variables)
                final_optimizer.apply_gradients(zip(final_gradients, final_model.trainable_variables))
            final_losses.append(final_loss)
            metric.update_state(y_batch, final_out)
            final_accuracy.append(metric.result())
            metric.reset_states()

            # record the loss and accuracy of single models
            mic_loss = loss_function(y_batch, mic_out)
            mic_losses.append(mic_loss)
            metric.update_state(y_batch, mic_out)
            mic_accuracy.append(metric.result())
            metric.reset_states()

            acc_x_loss = loss_function(y_batch, acc_x_out)
            acc_x_losses.append(acc_x_loss)
            metric.update_state(y_batch, acc_x_out)
            acc_x_accuracy.append(metric.result())
            metric.reset_states()

            acc_y_loss = loss_function(y_batch, acc_y_out)
            acc_y_losses.append(acc_y_loss)
            metric.update_state(y_batch, acc_y_out)
            acc_y_accuracy.append(metric.result())
            metric.reset_states()

            acc_z_loss = loss_function(y_batch, acc_z_out)
            acc_z_losses.append(acc_z_loss)
            metric.update_state(y_batch, acc_z_out)
            acc_z_accuracy.append(metric.result())
            metric.reset_states()

            laser_loss = loss_function(y_batch, laser_out)
            laser_losses.append(laser_loss)
            metric.update_state(y_batch, laser_out)
            laser_accuracy.append(metric.result())
            metric.reset_states()

        print("Over Train Dataset")
        print(f"final accuracy: {numpy.sum(final_accuracy) / len(final_accuracy)}, "
              f"loss:{numpy.sum(final_losses) / len(final_losses)}")
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
            x_batch = data_batch['data'].numpy().reshape((-1, arg.feature_row, arg.feature_column, 1))
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

            # concat the output of single models as the input of final model
            final_input = tf.concat([mic_out, acc_x_out, acc_y_out, acc_z_out, laser_out], 1)

            final_out = final_model(final_input)
            final_loss = loss_function(y_batch, final_out)
            final_losses.append(final_loss)
            metric.update_state(y_batch, final_out)
            final_accuracy.append(metric.result())
            metric.reset_states()

        print("Over Test Dataset")
        print(f"final accuracy: {numpy.sum(final_accuracy) / len(final_accuracy)}, "
              f"loss:{numpy.sum(final_losses) / len(final_losses)}")
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

        tf.saved_model.save(final_model, f"models/tensorflow/{arg.database}/{arg.activity}/final")
















