import smtplib
import ssl

def send_email_alert():
    sender_email = "your_email@gmail.com"
    receiver_email = "parent_email@gmail.com"
    password = "GENERATED_APP_PASSWORD"

    subject = "🚨 Alert: Child Tried to Access Blocked Content!"
    body = "Warning! A child attempted to access a restricted website."

    message = f"Subject: {subject}\n\n{body}"

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

