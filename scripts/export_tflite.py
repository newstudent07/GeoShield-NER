import os
import torch
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vision.classifier import get_model

MODEL_DIR = "models"
ONNX_PATH = os.path.join(MODEL_DIR, "crack_detector.onnx")
TFLITE_PATH = os.path.join(MODEL_DIR, "crack_detector.tflite")

def export_to_onnx(model):
    """Exports PyTorch model to ONNX."""
    print("Exporting PyTorch model to ONNX...")
    dummy_input = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        model, 
        dummy_input, 
        ONNX_PATH, 
        input_names=["input"], 
        output_names=["output"],
        opset_version=13
    )
    print(f"ONNX model saved to {ONNX_PATH}")

def convert_onnx_to_tflite():
    """Converts ONNX to TFLite and validates via interpreter."""
    try:
        import tensorflow as tf
        import onnx2tf
    except ImportError:
        print("TensorFlow or onnx2tf is not installed in the current environment.")
        print("Skipping TFLite conversion. Please run this script in an environment with TF.")
        return

    print("Converting ONNX to TFLite...")
    # onnx2tf provides a python API to convert onnx to saved_model/tflite
    onnx2tf.convert(
        input_onnx_file_path=ONNX_PATH,
        output_folder_path=MODEL_DIR,
        copy_onnx_input_output_names_to_tflite=True,
        non_verbose=True
    )
    
    # Typically, onnx2tf outputs saved_model in the folder, and we convert that to TFLite
    saved_model_dir = os.path.join(MODEL_DIR, "saved_model")
    if os.path.exists(saved_model_dir):
        converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    else:
        # Some versions output .tflite directly or require Keras model
        print("Expected saved_model from onnx2tf, assuming direct export.")
        return

    # Check 2 constraint: Catch and resolve "Unsupported Operator" errors
    # By enabling SELECT_TF_OPS, we handle operators that aren't natively supported by TFLite's builtin ops.
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    tflite_model = converter.convert()
    
    with open(TFLITE_PATH, "wb") as f:
        f.write(tflite_model)
    print(f"TFLite model saved to {TFLITE_PATH}")

    validate_tflite()

def validate_tflite():
    """Validates the TFLite model using a dummy inference array."""
    try:
        import tensorflow as tf
        import numpy as np
    except ImportError:
        return
        
    print("Validating TFLite model with dummy inference...")
    try:
        interpreter = tf.lite.Interpreter(model_path=TFLITE_PATH)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Create a dummy array matching input shape
        input_shape = input_details[0]['shape']
        dummy_data = np.random.rand(*input_shape).astype(np.float32)
        
        interpreter.set_tensor(input_details[0]['index'], dummy_data)
        interpreter.invoke()
        
        output_data = interpreter.get_tensor(output_details[0]['index'])
        print(f"Validation successful. Dummy output shape: {output_data.shape}")
        
    except Exception as e:
        print(f"TFLite validation failed: {e}")
        print("Note: If 'Unsupported Operator' error, ensure SELECT_TF_OPS is enabled in export.")

def main():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    model = get_model()
    export_to_onnx(model)
    convert_onnx_to_tflite()

if __name__ == "__main__":
    main()
