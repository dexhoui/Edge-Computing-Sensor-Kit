import os, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # /source
SOURCE_DIR = os.path.dirname(SCRIPT_DIR) # /server
ROOT_DIR = os.path.dirname(SOURCE_DIR)
sys.path.append(SOURCE_DIR)
sys.path.append(ROOT_DIR)
print("# function     : creat train data list")
print("# current path :", SCRIPT_DIR)
print("# source  path :", SOURCE_DIR)
print("# root    path :", ROOT_DIR)

scene = "350"
activity = "spin"
# model arguments
BATCH_SIZE = 64
NUM_EPOCHS = 10

# dataset arguments
feature_row = 60
feature_column = 91
mic_column = 66
acc_x_column = 8
acc_y_column = 8
acc_z_column = 8

mic_end = 66
acc_x_end = 74
acc_y_end = 82
acc_z_end = 90
laser_end = 91

# raw data path
raw_data_path = f"{SOURCE_DIR}/dataset/raw_data/{scene}/{activity}/"
data_list_path = f"{SOURCE_DIR}/dataset/data_list/{scene}/{activity}/"


train_path = f"{SOURCE_DIR}/dataset/tfrecords/{scene}/{activity}/train.tfrecord"
test_path = f"{SOURCE_DIR}/dataset/tfrecords/{scene}/{activity}/test.tfrecord"

tensorflow_model_path = f"{SOURCE_DIR}/models/tensorflow/{scene}/{activity}"
tflite_model_path = f"{SOURCE_DIR}/models/tflite/{scene}/{activity}"