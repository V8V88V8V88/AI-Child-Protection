# AI Child Protection Monitor

This project uses face recognition and age estimation to detect if a child is using the computer.
If a child (estimated age < 18) is detected, it attempts to block a predefined list of websites
by modifying the system's hosts file and sends an email alert.

## Project Structure

```
.
├── data/
│   └── family_dataset/   # Stores captured face images for known users
├── models/
│   ├── age_model.h5      # Pre-trained age estimation model
│   ├── face_recognition_model.pkl # Trained KNN face recognizer
│   └── label_map.pkl     # Maps numeric labels to names
├── src/
│   ├── __init__.py
│   ├── dataset_creator_gui.py # GUI for capturing face images
│   ├── main_gui.py          # Main application GUI
│   ├── face_operations/     # Face detection/recognition/age logic
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   └── training.py
│   └── system_actions/      # Website blocking and email logic
│       ├── __init__.py
│       ├── host_blocker.py
│       └── email_notifier.py
├── .venv/                   # Python virtual environment (recommended)
├── README.md                # This file
├── requirements.txt         # Project dependencies
└── run_main_app.py          # Script to launch the main GUI
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd AI-Child-Protection
    ```

2.  **Create and Activate Virtual Environment (Recommended):**
    *   Ensure you have a compatible Python version installed (e.g., Python 3.11 was used during development, as TensorFlow may not support the latest Python).
    ```bash
    python3.11 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .\.venv\Scripts\activate # Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Obtain Age Model:**
    *   You need a pre-trained age estimation model named `age_model.h5`.
    *   Place this file inside the `models/` directory.
    *   Models trained on the UTKFace dataset are commonly used.

5.  **Configure Email:**
    *   Edit `src/system_actions/email_notifier.py`.
    *   Set the `sender_email`, `receiver_email`.
    *   Replace `"GENERATED_APP_PASSWORD"` with a 16-character Google App Password for the `sender_email` account (requires 2-Step Verification enabled).

## Usage

1.  **Create Face Dataset:**
    *   Run the dataset creator GUI:
        ```bash
        python src/dataset_creator_gui.py
        ```
    *   Follow the prompts to enter the number of members and capture 10 face images for each.
    *   Images will be saved in `data/family_dataset/`.

2.  **Train Face Recognizer:**
    *   Run the training script:
        ```bash
        python src/face_operations/training.py
        ```
    *   This will create/update `face_recognition_model.pkl` and `label_map.pkl` in the `models/` directory.

3.  **Run Main Application:**
    *   **IMPORTANT:** This application modifies the system hosts file and requires **administrator/root privileges** to function correctly.
    *   **Linux/macOS:**
        ```bash
        sudo python run_main_app.py
        ```
    *   **Windows:** Run your terminal (Command Prompt, PowerShell, etc.) **as Administrator**, navigate to the project directory, activate the virtual environment, and then run:
        ```bash
        python run_main_app.py
        ```
    *   Click "Start Monitoring" in the GUI.

## Notes

*   **Age Estimation Accuracy:** Age estimation models can be inaccurate depending on lighting, face angle, and individual variation. The `< 18` threshold might need adjustment.
*   **Website Blocking:** Modifying the hosts file is a basic blocking method and can be bypassed. Network-level filtering or dedicated parental control software offers more robust solutions.
*   **Permissions:** Remember the need for elevated privileges when running the main application.
