# AI-Child-Protection
This AI-driven parental control system ensures online safety for children by integrating face detection, website blocking, and real-time alerts into one automated solution. Unlike traditional parental controls, this system adapts dynamically based on who is using the device and applies restrictions accordingly.

🔹 How It Works

✅ Face Detection: Uses AI to recognize whether a child or adult is using the device.✅ Age Estimation: Deep learning models estimate the user’s age in real-time.✅ Dynamic Content Blocking: Automatically blocks inappropriate websites when a child is detected.✅ Parental Alerts: Sends instant email notifications to parents if a child tries to access restricted content.

🔹 Why This Project is Different from Traditional Parental Controls

1️⃣ Face Detection-Based Access Control

✅ Your Project: Uses AI-powered facial recognition to identify children and enforce restrictions.❌ Traditional Controls: Require manual setup, and restrictions apply to the entire device regardless of the user.

2️⃣ Real-Time Content Blocking

✅ Your Project: Dynamically blocks or unblocks content based on who is using the device at that moment.❌ Traditional Controls: Work on predefined settings that apply all the time unless changed manually.

3️⃣ Automatic Switching Between Child & Adult Modes

✅ Your Project: Instantly adapts to a new user (child/adult) using real-time face recognition.❌ Traditional Controls: Require passwords, PINs, or time-based restrictions that children might bypass.

4️⃣ AI-Based Age Estimation

✅ Your Project: Uses machine learning to estimate the user's age and apply appropriate filters.❌ Traditional Controls: Depend on pre-set user profiles and manual age inputs.

5️⃣ Security & Monitoring

✅ Your Project:

Sends real-time alerts to parents if a child tries to access restricted content.

Uses biometric authentication to prevent unauthorized access.
❌ Traditional Controls:

Only provide activity logs that parents check after the child has already accessed content.

6️⃣ More Adaptive & Harder to Bypass

✅ Your Project: Even if a child resets the device or switches accounts, AI-based face detection still enforces restrictions.❌ Traditional Controls: Can often be bypassed by resetting the device, using incognito mode, or switching accounts.

🔹 Key Components of the Project

1️⃣ Face Detection Script (face_detection.py)

📌 Purpose: Detects faces via webcam and determines if the user is a child or adult.📌 Technology Used: OpenCV, DeepFace AI.

2️⃣ Website Blocking Script (block_websites.py)

📌 Purpose: Prevents access to harmful websites when a child is detected.📌 Technology Used: Modifies the system’s hosts file to block adult sites.

3️⃣ Email Alert Script (emailalert.py)

📌 Purpose: Sends real-time email notifications to parents when a child attempts to access restricted content.📌 Technology Used: Python’s smtplib for sending emails.

4️⃣ Integrated AI Controller (ai.py)

📌 Purpose: Combines all functionalities into a single automated process. It detects faces, estimates age, blocks sites if necessary, and alerts parents in real time.
