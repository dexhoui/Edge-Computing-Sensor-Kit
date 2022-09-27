#!/usr/bin/env python3.7.9
'''
Copyright © 2021 DUE TUL
@ desc  : This modules is used to define the data read function
@ author: BOHAO CHU
'''
import arguments as arg
import tensorflow as tf


def _parse_data_function(example):
    data_feature_description = {
        # (128, 200)
        'data': tf.io.FixedLenFeature([arg.feature_row * arg.feature_column], tf.float32),
        'label': tf.io.FixedLenFeature([], tf.int64),
    }
    return tf.io.parse_single_example(example, data_feature_description)


def train_reader_tfrecord(data_path, num_epochs, batch_size=128):
    raw_dataset = tf.data.TFRecordDataset(data_path)
    train_dataset = raw_dataset.map(_parse_data_function)      # 解析
    train_dataset = train_dataset.repeat(count=num_epochs)     # 复制
    train_dataset = train_dataset.shuffle(buffer_size=1000)    # 打乱
    train_dataset = train_dataset.batch(batch_size=batch_size) # 分批
    train_dataset = train_dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
    return train_dataset


def test_reader_tfrecord(data_path, batch_size=128):
    raw_dataset = tf.data.TFRecordDataset(data_path)
    test_dataset = raw_dataset.map(_parse_data_function)
    test_dataset = test_dataset.batch(batch_size=batch_size)
    return test_dataset
