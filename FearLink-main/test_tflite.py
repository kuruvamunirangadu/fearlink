import numpy as np
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def generate_test_data(stress_level):
    if stress_level == "calm":
        ppg = np.full((1, 50, 1), 70) / 120
        gsr = np.full((1, 50, 1), 1.0) / 3.0
        accel = np.random.uniform(0.0, 0.2, (1, 150, 3)) / 1.5
    else:  # fear
        ppg = np.linspace(90, 120, 50).reshape(1, 50, 1) / 120
        gsr = np.linspace(2.0, 3.0, 50).reshape(1, 50, 1) / 3.0
        accel = np.random.uniform(0.5, 1.5, (1, 150, 3)) / 1.5
    return ppg.astype(np.float32), gsr.astype(np.float32), accel.astype(np.float32)

def predict_fear(ppg, gsr, accel):
    interpreter.set_tensor(input_details[0]['index'], accel) # [1, 150, 3]
    interpreter.set_tensor(input_details[1]['index'], ppg)   # [1, 50, 1]
    interpreter.set_tensor(input_details[2]['index'], gsr)   # [1, 50, 1]
    interpreter.invoke()
    fear_score = interpreter.get_tensor(output_details[0]['index'])[0][0]
    return fear_score

calm_ppg, calm_gsr, calm_accel = generate_test_data("calm")
fear_ppg, fear_gsr, fear_accel = generate_test_data("fear")

calm_score = predict_fear(calm_ppg, calm_gsr, calm_accel)
fear_score = predict_fear(fear_ppg, fear_gsr, fear_accel)

print(f"Calm Score: {calm_score * 100:.2f}%")
print(f"Fear Score: {fear_score * 100:.2f}%")