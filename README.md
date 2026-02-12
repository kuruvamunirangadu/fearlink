# FearLink

FearLink is a wearable-focused research prototype that explores stress and fear detection from wrist-worn sensors. The repository bundles the training pipeline used to fine-tune a lightweight deep neural network on the WESAD dataset, multiple desktop dashboards for live visualisation, and an on-device TensorFlow Lite model suitable for edge deployment on a smartwatch companion app.

## Highlights

- End-to-end workflow covering data preparation, model training, evaluation, and TensorFlow Lite conversion in [FearLink-main/train.py](FearLink-main/train.py).
- Real-time PyQt5 demo experiences for showcasing the model, ranging from a minimal proof-of-concept in [FearLink-main/realtime_stress_detection.py](FearLink-main/realtime_stress_detection.py) to an immersive dashboard in [FearLink-main/fear_dashboard_final_3.py](FearLink-main/fear_dashboard_final_3.py).
- Pre-trained TensorFlow Lite model at [FearLink-main/model.tflite](FearLink-main/model.tflite) and auxiliary diagnostics such as [FearLink-main/training_log.txt](FearLink-main/training_log.txt) and [FearLink-main/training_history.png](FearLink-main/training_history.png).
- Pitch materials and PCB prototypes that contextualise the project rollout for investors and hardware partners (see [FearLink-main/Investor_Pitch.pdf](FearLink-main/Investor_Pitch.pdf) and [FearLink-main/FearLink_PCB_Layout.pdf](FearLink-main/FearLink_PCB_Layout.pdf)).

## Repository Layout

```
FearLink-main/
├── FearLink-main/            # Application, training scripts, dashboards, assets
│   ├── fear_dashboard_final_3.py
│   ├── realtime_stress_detection.py
│   ├── train.py
│   ├── model.tflite
│   ├── training_log.txt
│   ├── Investor_Pitch.pdf
│   └── ... additional prototypes and utilities
└── README.md
```

The working Python sources reside inside the nested `FearLink-main` directory. Navigate into that folder before running any script.

## Getting Started

```bash
# Clone the project
git clone https://github.com/kuruvamunirangadu/fearlink.git
cd fearlink/FearLink-main

# Optional: create an isolated environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux

# Install runtime dependencies
pip install -r requirements.txt  # Create your own list or install packages listed below
```

### Core Dependencies

The scripts refer to the following Python packages:

- tensorflow>=2.13
- numpy, scipy, scikit-learn
- matplotlib
- PyQt5 (PyQtChart module is required for the dashboards)

Install them manually if you are not using a `requirements.txt` file:

```bash
pip install tensorflow numpy scipy scikit-learn matplotlib PyQt5 PyQt5-sip
```

## Training Pipeline

1. Download the WESAD dataset (https://archive.ics.uci.edu/dataset/505/wesad) and extract it locally.
2. Update the `data_dir` constant near the top of [FearLink-main/train.py](FearLink-main/train.py) so it points to your copy of the dataset.
3. From inside `FearLink-main`, launch the training script:
   ```bash
   python train.py
   ```
4. Monitor progress through console output or by tailing [FearLink-main/training_log.txt](FearLink-main/training_log.txt). The script saves the learning curves to [FearLink-main/training_history.png](FearLink-main/training_history.png) and exports an updated TensorFlow Lite model to [FearLink-main/model.tflite](FearLink-main/model.tflite).

The training routine performs windowing, class balancing, normalisation, model fitting, evaluation, and automatic conversion to TensorFlow Lite with basic optimisations suitable for edge inference.

## Running the Desktop Demos

- **Real-time stress detection sandbox**
  ```bash
  python realtime_stress_detection.py
  ```
  This QMainWindow synthesises PPG, GSR, and accelerometer samples, feeds them into the TensorFlow Lite interpreter, and visualises predictions with an adjustable decision threshold.

- **Immersive dashboard experience**
  ```bash
  python fear_dashboard_final_3.py
  ```
  This elaborate PyQt5 dashboard animates vitals, tabular history, and timelines while handling SOS escalation logic. Ensure the PyQtChart bindings are available in your environment.

Additional prototypes (`fear_dashboard.py`, `fear_dashboard_2.py`, `Investor_Pitch.py`, etc.) demonstrate design explorations and can be run in the same fashion.

## Evaluating the TensorFlow Lite Model

Use [FearLink-main/test_tflite.py](FearLink-main/test_tflite.py) as a quick smoke test that compares calm versus fear scenarios using synthetic samples:

```bash
python test_tflite.py
```

The script prints fear scores for both cases, confirming that the lite model responds meaningfully to changes in physiological signals.

## Logs and Telemetry

- [FearLink-main/training_log.txt](FearLink-main/training_log.txt) captures training diagnostics, including class balance, metric progression, and TFLite metadata.
- [FearLink-main/sos_log.txt](FearLink-main/sos_log.txt) records SOS events triggered from the dashboard UI. Clear or rotate the log before running public demos.

## Roadmap Ideas

- Port the Qt dashboards to a cross-platform framework (e.g., Flutter or React Native with Pyodide backend) for tighter smartwatch integration.
- Replace synthetic data streams with Bluetooth feeds from the production hardware.
- Extend the training pipeline with additional affective datasets and experiment with knowledge distillation to further compress the edge model.

## License

Specify project licensing terms here (MIT, Apache-2.0, proprietary, etc.). Update this section once a decision is made.
