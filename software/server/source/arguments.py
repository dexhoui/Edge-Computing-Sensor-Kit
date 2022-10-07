scene = "350"
activity = "on"
# model arguments
BATCH_SIZE = 512
NUM_EPOCHS = 50

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
raw_data_path = f"../dataset/raw_data/{scene}/{activity}/"
data_list_path = f"../dataset/data_list/{scene}/{activity}/"


train_path = f"../dataset/tfrecords/{scene}/{activity}/train.tfrecord"
test_path = f"../dataset/tfrecords/{scene}/{activity}/test.tfrecord"
