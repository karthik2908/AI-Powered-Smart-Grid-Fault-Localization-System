"""
AI Model Training & Inference Pipeline for Smart Grid Electrical Fault Classification.
Classes:
  0: Normal / Healthy Operation
  1: Short Circuit (Line-to-Ground / Phase Fault)
  2: Physical Cable Cut (Open Circuit)
  3: Overload / High Impedance Thermal Fault
"""

import os
import numpy as np
import pickle

# Check for TensorFlow availability
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


FAULT_LABELS = {
    0: "Normal (Healthy)",
    1: "Short Circuit (Ground / Phase Fault)",
    2: "Physical Cable Cut (Open Circuit)",
    3: "Overload / High Impedance Thermal Stress"
}


def generate_synthetic_grid_dataset(samples_per_class=2500, random_seed=42):
    """
    Generates realistic synthetic electrical grid telemetry dataset based on
    transient and steady-state electrical characteristics.
    Features: [Voltage, Current, Delta_Voltage, Delta_Current, Frequency, Power_Factor]
    """
    np.random.seed(random_seed)
    X = []
    y = []

    # 1. Class 0: Normal / Healthy
    for _ in range(samples_per_class):
        v = np.random.normal(230.0, 4.0)
        i = np.random.uniform(2.0, 14.0)
        dv = np.random.normal(0.0, 1.5)
        di = np.random.normal(0.0, 0.8)
        freq = np.random.normal(50.0, 0.1)
        pf = np.random.uniform(0.92, 0.99)
        X.append([v, i, dv, di, freq, pf])
        y.append(0)

    # 2. Class 1: Short Circuit
    for _ in range(samples_per_class):
        v = np.random.uniform(10.0, 55.0)
        i = np.random.uniform(32.0, 75.0)
        dv = np.random.uniform(-220.0, -160.0)
        di = np.random.uniform(20.0, 60.0)
        freq = np.random.normal(49.2, 0.8)
        pf = np.random.uniform(0.15, 0.45)
        X.append([v, i, dv, di, freq, pf])
        y.append(1)

    # 3. Class 2: Physical Cable Cut
    for _ in range(samples_per_class):
        v = np.random.uniform(0.0, 12.0)
        i = np.random.uniform(0.0, 0.2)
        dv = np.random.uniform(-235.0, -210.0)
        di = np.random.uniform(-15.0, -3.0)
        freq = np.random.uniform(0.0, 15.0)
        pf = 0.0
        X.append([v, i, dv, di, freq, pf])
        y.append(2)

    # 4. Class 3: Overload / Thermal Stress
    for _ in range(samples_per_class):
        v = np.random.uniform(185.0, 212.0)
        i = np.random.uniform(18.0, 31.0)
        dv = np.random.uniform(-40.0, -15.0)
        di = np.random.uniform(6.0, 18.0)
        freq = np.random.normal(49.6, 0.3)
        pf = np.random.uniform(0.72, 0.86)
        X.append([v, i, dv, di, freq, pf])
        y.append(3)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)

    # Shuffle
    indices = np.arange(len(y))
    np.random.shuffle(indices)
    return X[indices], y[indices]


def build_neural_network_model(input_dim=6, num_classes=4):
    """
    Constructs a Multi-Layer Perceptron (MLP) architecture optimized for
    fast inference on cloud backends or conversion to Edge TFLite for ESP32.
    """
    if not TF_AVAILABLE:
        return None

    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001)),
        layers.BatchNormalization(),
        layers.Dropout(0.2),

        layers.Dense(32, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.15),

        layers.Dense(16, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def train_and_export_model(output_dir="model_weights"):
    """
    Executes dataset generation, model compilation, training, and artifact export.
    """
    os.makedirs(output_dir, exist_ok=True)
    X, y = generate_synthetic_grid_dataset(samples_per_class=3000)

    # Train / Test split
    split_idx = int(0.8 * len(y))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Normalization statistics
    mean = np.mean(X_train, axis=0)
    std = np.std(X_train, axis=0) + 1e-7

    # Save normalization stats
    stats_path = os.path.join(output_dir, "scaler_stats.pkl")
    with open(stats_path, "wb") as f:
        pickle.dump({"mean": mean, "std": std}, f)

    X_train_norm = (X_train - mean) / std
    X_test_norm = (X_test - mean) / std

    if TF_AVAILABLE:
        model = build_neural_network_model(input_dim=6, num_classes=4)
        print("Training Neural Network...")
        history = model.fit(
            X_train_norm, y_train,
            validation_data=(X_test_norm, y_test),
            epochs=25,
            batch_size=64,
            verbose=1
        )
        test_loss, test_acc = model.evaluate(X_test_norm, y_test, verbose=0)
        print(f"Test Accuracy: {test_acc * 100:.2f}%")

        model_path = os.path.join(output_dir, "fault_classifier.keras")
        model.save(model_path)
        print(f"Model saved to {model_path}")
        return model, (mean, std)
    else:
        print("TensorFlow not installed. Stored normalization stats for rule-based classifier.")
        return None, (mean, std)


def classify_grid_fault(voltage, current, delta_v, delta_i, frequency=50.0, power_factor=0.95):
    """
    Production inference function used by the Django backend and simulated tests.
    Returns: (fault_type: int, confidence: float, summary: str)
    """
    # 1. Explicit Physical Heuristic Safeguards (fast-path)
    if voltage < 20.0 and abs(current) < 0.3:
        return 2, 0.992, "Physical Cable Cut: Near-zero voltage potential with total open-circuit loss."

    if current > 28.0 or (delta_i > 18.0 and voltage < 70.0):
        return 1, 0.985, "Short Circuit: Catastrophic current surge accompanied by steep voltage depression."

    if (current > 16.5 and voltage < 205.0) or (current > 22.0):
        return 3, 0.941, "Overload Fault: Sustained thermal overcurrent exceeding distribution transformer rating."

    # 2. Normal State
    if 210.0 <= voltage <= 245.0 and current <= 15.0:
        return 0, 0.995, "Normal: Operating within standard nominal grid parameters."

    # 3. Soft Heuristic Classification
    if voltage < 180.0 and current > 15.0:
        return 3, 0.912, "High Impedance Overload Stress."
    elif voltage < 80.0:
        return 2, 0.925, "Incipient Open Circuit / Phase Discontinuity."

    return 0, 0.970, "Normal: Minor transient fluctuation."


if __name__ == '__main__':
    train_and_export_model()
