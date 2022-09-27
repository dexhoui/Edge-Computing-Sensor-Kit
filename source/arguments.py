activity = "on"
# model arguments
BATCH_SIZE = 512
NUM_EPOCHS = 50

# dataset arguments
feature_row = 64
feature_column = 57
mic_column = 41
acc_x_column = 5
acc_y_column = 5
acc_z_column = 5

mic_end = 41
acc_x_end = 46
acc_y_end = 51
acc_z_end = 56
laser_end = 57

# raw data path
raw_data_path = f"../dataset/raw_data/{activity}/"
data_list_path = f"../dataset/data_list/{activity}/"

train_path = f"dataset/tfrecords/{activity}/train.tfrecord"
test_path = f"dataset/tfrecords/{activity}/test.tfrecord"
