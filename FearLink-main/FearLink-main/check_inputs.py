import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Input Details:")
for i, detail in enumerate(input_details):
    print(f"Input {i}: {detail['name']}, Shape: {detail['shape']}")
print("Output Details:", output_details)