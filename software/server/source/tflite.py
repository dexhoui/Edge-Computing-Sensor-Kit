import tensorflow as tf
import reader
import arguments as arg
import pathlib
'''
train_dataset = reader.train_reader_tfrecord(
    data_path=config.trainpath,
    num_epochs=1,
    batch_Size=128)


for batch_idx, data_batch in enumerate(train_dataset):
    global data
    data = data_batch['data'].numpy().reshape(-1, 128, 54, 1)
    break

def representative_data_gen():
    global data
    for input_value in tf.data.Dataset.from_tensor_slices(data).batch(1).take(100):
        yield [input_value]

converter = tf.lite.TFLiteConverter.from_saved_model("saved_model/")
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_data_gen
# Ensure that if any ops can't be quantized, the converter throws an error
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
# Set the input and output tensors to uint8 (APIs added in r2.3)
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8
tflite_model_quant = converter.convert()


# Save the model.
tflite_models_dir = pathlib.Path("tflite_models/")
tflite_models_dir.mkdir(exist_ok=True, parents=True)

# Save the quantized model:
tflite_model_quant_file = tflite_models_dir/"model_quant.tflite"
tflite_model_quant_file.write_bytes(tflite_model_quant)
print("OK")

'''
for m in ['final']:
  # Convert the model
  converter = tf.lite.TFLiteConverter.from_saved_model(f"{arg.tensorflow_model_path}/{m}")  # path to the SavedModel directory
  tflite_model = converter.convert()
  # Save the model.
  with open(f'{arg.tflite_model_path}.tflite', 'wb') as f:
    f.write(tflite_model)
  print(f"{arg.activity} tflite model converted !")