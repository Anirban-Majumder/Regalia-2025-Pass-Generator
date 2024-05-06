from email.mime.image import MIMEImage
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
import csv
import qrcode
import pyqrcode
import json
from pass_gen import pass_gen

load_dotenv()
# Set up the email parameters
sender = "rcciit.regalia.official@gmail.com"
subject = "Regalia 2024 - Please go through the email carefully"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

app_password = os.getenv("APP_PASSWORD")
sender_email= os.getenv("SENDER_EMAIL")
# Log in to the SMTP server
server = smtplib.SMTP(sender_email, 587)
server.starttls()
server.login(sender, app_password)
print("Login successful")



def makeQR(data):
    qr = pyqrcode.create(data)
    qr.png('qr_code.png', scale=30, module_color='#03045E', background='#538EFF')
    return qr.get_png_size(30)


# Open the log file in write mode to clear any existing content
with open("log.txt", "w") as log:
    pass  # Clears the existing content of log.txt

# Open the CSV file
with open("data.csv", "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter="\t")
    print("Opened CSV file")
    # Skip the header row
    next(reader)
    # Open the log file in append mode
    with open("log.txt", "a") as log:
        print("Opened log file")
        email_count = 0  # Initialize email count
        # Loop through each row in the CSV file
        for i, row in enumerate(reader, start=1):  # Start counting from 1
            print(f"Processing row {i}: {row}")
            try:
                # Add data to the QR code
                # qr.add_data([row[0], row[2], row[3]])
                qr.add_data(json.dumps({"name": row[0], "phone":row[1], "email": row[2], "roll": row[3]}))
                qr.make(fit=True)

                # Create an image from the QR code
                img = qr.make_image(fill_color="black", back_color="white")

                # Save the image as a PNG file
                img.save("qr_code.png")

                # resets qr code data
                qr.clear()

                # Open the image file and read its contents
                with open("qr_code.png", "rb") as f:
                    img_data = f.read()

                # Create the message
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = row[2]
                msg["Subject"] = subject

                # Attach email content and QR code image
                msg.attach(MIMEText(pass_gen(row[0], row[1], row[2]), "html"))
                msg.attach(MIMEImage(img_data, name="pass_qr.png"))

                # Send the message
                server.sendmail(sender, row[2], msg.as_string())
                print("sent -> " + row[2])
                # Append a new line to the file with the index and email address
                log.write(f"{i}: sent -> {row[2]}\n")
                email_count += 1  # Increment email count

            except Exception as e:
                print("failed -> " + row[2] + str(e))
                log.write(f"{i}: failed -> {row[2]} {str(e)}\n")

# Print the total number of emails sent
print(f"Total emails sent: {email_count}")

# Close the SMTP server
server.quit()
