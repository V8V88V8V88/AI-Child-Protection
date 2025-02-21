import subprocess  # To run the Face Detection script
import block_websites  # Import website blocking script
import emailalert  # Import email alert script

def main():
    print("🔹 Starting AI-Child-Protection System...")

    # Step 1: Run the Face Detection script
    print("🔹 Running Face Detection...")
    result = subprocess.run(["python", "FACE DETECTION NEW.py"], capture_output=True, text=True)

    # Check if the face detection script indicates content restriction
    if "🔴 Content is Restricted" in result.stdout:
        print("🔹 Child detected! Proceeding with website blocking and email alert...")

        # Step 2: Block Websites
        block_websites.block_sites()

        # Step 3: Send Email Alert
        emailalert.send_email_alert()

    else:
        print("✅ No child detected. No action taken.")

if __name__ == "__main__":
    main()
