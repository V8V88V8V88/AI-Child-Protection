# AI Child Protection Monitor

This project uses face recognition and age estimation to detect if a child is using the computer.
If a child (estimated age < 18) is detected, it attempts to block a predefined list of websites
by modifying the system's hosts file, creating browser extensions, and setting up a persistent
blocking service.

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
│   ├── password_dialog.py   # Parent password protection
│   ├── face_operations/     # Face detection/recognition/age logic
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   └── training.py
│   └── system_actions/      # Website blocking and email logic
│       ├── __init__.py
│       ├── host_blocker.py
│       ├── browser_extension.py
│       ├── block_service.py
│       └── email_notifier.py
├── .venv/                   # Python virtual environment
├── README.md                # This file
├── requirements.txt         # Project dependencies
├── run_main_app.py          # Script to launch the main GUI
└── run_with_sudo.sh         # Helper script for Linux/macOS to run with sudo while preserving venv
```

## Installation

### Prerequisites

- Python 3.9+ (3.9-3.11 recommended as TensorFlow may not fully support the latest Python versions)
- Git
- Administrator/root privileges (required for website blocking functionality)
- OpenCV dependencies (see OS-specific instructions below)

### Step 1: Clone the Repository

```bash
git clone https://github.com/V8V88V8V88/AI-Child-Protection.git
cd AI-Child-Protection
```

### Step 2: Set Up Virtual Environment

#### Windows

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### OS-Specific OpenCV Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y libsm6 libxext6 libxrender-dev libgl1-mesa-glx
```

**Fedora:**
```bash
sudo dnf install -y libglvnd-glx mesa-libGL
```

**macOS:**
```bash
brew install cmake pkg-config
```

**Windows:**
Most dependencies are included in the pip packages, but you may need Microsoft Visual C++ Redistributable if you encounter DLL errors.

### Step 4: Obtain or Train Age Model

You need a pre-trained age estimation model named `age_model.h5`. Place this file inside the `models/` directory. 

If you don't have an age model:
1. You can train one using the UTKFace dataset
2. Or download a pre-trained model from [this link](https://www.example.com/age_model.h5) (example link)

### Step 5: Configure Email Notifications (Optional)

Edit `src/system_actions/email_notifier.py`:
- Set `sender_email` and `receiver_email`
- Replace `"GENERATED_APP_PASSWORD"` with a 16-character Google App Password (requires 2-Step Verification enabled)

## Running the Application

### Create Face Dataset (First-time Setup)

Before using the application, you need to create a dataset of family members' faces and train the recognizer:

```bash
# Inside activated virtual environment
python src/dataset_creator_gui.py
```

Follow the prompts to capture images for each family member. Then train the recognizer:

```bash
python src/face_operations/training.py
```

### Running the Main Application

The application requires administrator/root privileges to modify the hosts file and set up blocking services.

#### Windows

1. Open Command Prompt or PowerShell **as Administrator**
2. Navigate to the project directory
3. Activate the virtual environment
   ```
   .\.venv\Scripts\activate
   ```
4. Run the application
   ```
   python run_main_app.py
   ```

#### macOS

Use the provided helper script:
```bash
chmod +x run_with_sudo.sh  # Make it executable (first-time only)
./run_with_sudo.sh
```

#### Linux

Use the provided helper script which preserves your virtual environment when running with sudo:
```bash
chmod +x run_with_sudo.sh  # Make it executable (first-time only)
./run_with_sudo.sh
```

If you encounter issues with the script, you can run manually:
```bash
sudo $(which python) run_main_app.py
```

## Using the Application

### Main Features

1. **Monitor Tab**: Detects faces and estimates age to identify children
   - Click "Start Monitoring" to begin detection
   - If a child is detected, websites will be automatically blocked

2. **Website Blocking Tab**: Manage website blocking (protected by parent password)
   - "Activate Website Blocking" - Blocks predefined websites
   - "Deactivate Website Blocking" - Removes blocking (requires password)
   - "Test Website Blocking" - Verifies blocking is working correctly
   - "Setup Browser Extensions" - Creates additional browser-level protection
   - "Install Service" - Sets up persistent protection that runs on system startup

3. **Manage Faces Tab**: Tools for face recognition
   - "Create Face Dataset" - Capture new faces
   - "Train Face Recognizer" - Update the face recognition model

### Important Notes About Website Blocking

- After activating blocking, you may need to:
  1. Clear your browser's DNS cache (browse to chrome://net-internals/#dns or restart Firefox)
  2. Clear your browser history/cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
  3. Restart your browser

- If the blocking service shows a removal error on Linux:
  1. Try running `sudo systemctl stop aichildprotection` manually
  2. Then `sudo systemctl disable aichildprotection`
  3. And finally `sudo rm /etc/systemd/system/aichildprotection.service`

## Troubleshooting

### Common Issues

1. **"Permission Denied" when blocking websites**
   - Ensure you're running the application with administrator/root privileges

2. **Face detection not working**
   - Check webcam permissions
   - Ensure good lighting conditions
   - Try running the dataset creator to verify camera access

3. **Websites still accessible after blocking**
   - Clear browser cache and DNS cache
   - Restart your browser
   - Check if the service is running properly

4. **Application crashes on startup**
   - Verify all dependencies are installed correctly
   - Check the age model is in the correct location
   - Ensure your Python version is compatible (3.9-3.11 recommended)

### Logs

- Application logs can be found in standard output
- Service logs (Linux): `/tmp/ai_child_protection_logs/block_service.log`
- Windows service: Check Windows Event Viewer

## Notes

- **Age Estimation Accuracy:** Age estimation models can be inaccurate depending on lighting, face angle, and individual variation. The `< 18` threshold might need adjustment.
- **Website Blocking:** While this application uses multiple layers of protection, determined users might still find ways to bypass it. Consider using additional parental control software for critical situations.
- **Permissions:** Remember the need for elevated privileges when running the main application.
- **Browser Support:** The browser extensions work with Chrome, Edge, Opera, and Firefox. Other browsers might only be protected by the host file blocking.

## Author

© 2025 Shristi Pandey
