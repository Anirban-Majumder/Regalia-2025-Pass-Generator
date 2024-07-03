from email.mime.image import MIMEImage
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageDraw, ImageFont
import csv
import qrcode
import pyqrcode
import json
from pass_gen import pass_gen

load_dotenv()
# Set up the email parameters
sender = "rcciit.regalia.official@gmail.com"
subject = "Regalia 2024 - Pass Details"
template = Image.open("pass_template.png")
detailsFont = ImageFont.truetype("Poppins-Regular.ttf", 40)
allowedFont = ImageFont.truetype("Poppins-SemiBold.ttf", 40)
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=20,
    border=4,
)

app_password = os.getenv("APP_PASSWORD")
sender_email = os.getenv("SENDER_EMAIL")
# Log in to the SMTP server
server = smtplib.SMTP(sender_email, 587)
server.starttls()
server.login(sender, app_password)
print("Login successful")


def makeQR(data):
    qr = pyqrcode.create(data)
    qr.png('qr_code.png', scale=10, module_color='#151515', background='#ffc82f')
    return qr.get_png_size(12)


# Open the log files in write mode to clear any existing content
with open("success_log.txt", "w") as success_log, open("failure_log.txt", "w") as failure_log:
    pass  # Clears the existing content of both log files

# Create a folder to save the passes if it doesn't exist
if not os.path.exists("passes"):
    os.makedirs("passes")

# Open the CSV file
with open("test2.csv", "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")  # Change delimiter to ","
    print("Opened CSV file")
    # Skip the header row
    next(reader)
    # Open the log files in append mode
    with open("success_log.txt", "a") as success_log, open("failure_log.txt", "a") as failure_log:
        print("Opened log files")
        email_count = 0  # Initialize email count
        # Loop through each row in the CSV file
        for i, row in enumerate(reader, start=1):  # Start counting from 1
            print(f"Processing row {i}: {row}")
            try:
                # Add data to the QR code
                qr_data = json.dumps({"name": row[0], "phone": row[1], "email": row[2], "roll": row[3]})
                cert = template.copy().convert("RGBA")  # Convert to RGBA
                draw = ImageDraw.Draw(cert)
                # qrcodes
                size = makeQR(qr_data)
                pos = ((600 - int(size / 2)), 50)
                qr_code_image = Image.open('qr_code.png').convert("RGBA")  # Convert to RGBA
                cert.paste(qr_code_image, pos, qr_code_image)  # Use the image as a mask for transparency
                # name
                # Calculate maximum width for the name text
                max_width = 1242  # Adjust this according to your template and requirements

                # Initial font size for the name
                nameFont = 150

                # Calculate the width of the text with the initial font size
                text_width = draw.textlength(row[0].upper(), ImageFont.truetype("Poppins-Bold.ttf", nameFont))

                # Calculate the difference from the maximum width
                difference = text_width - max_width
                # Define font size adjustments based on percentage difference
                if difference <= 0:
                    nameFont = 60
                elif 0 < difference <= max_width * 0.1:  # Adjust these thresholds as needed
                    nameFont = 70
                elif max_width * 0.1 < difference <= max_width * 0.2:
                    nameFont = 55
                elif max_width * 0.2 < difference <= max_width * 0.3:
                    nameFont = 45
                elif difference > max_width * 0.3:
                    nameFont = 45  # Adjust this for very large differences

                # Draw the text with the final font size
                draw.text(xy=(180, 850), text=row[0].upper(), fill='black', font=ImageFont.truetype("Poppins-Bold.ttf", nameFont))

                # email
                draw.text(xy=(180, 950), text=row[3], fill='black', font=detailsFont)
                # roll
                draw.text(xy=(180, 1020), text=row[1].upper(), fill='black', font=detailsFont)

                # Save the certificate with the name
                pass_filename = f"passes/{row[3].replace(' ', '_')}.png"
                cert.save(pass_filename)

                # Open the image file and read its contents
                with open(pass_filename, "rb") as f:
                    img_data = f.read()

                # Create the message
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = row[2]
                msg["Subject"] = row[0].upper() + ' - ' + subject

                # Attach email content and QR code image
                msg.attach(MIMEText(pass_gen(row[0], row[1], row[3]), "html"))
                msg.attach(MIMEImage(img_data, name="pass_qr.png"))

                # Send the message
                server.sendmail(sender, row[2], msg.as_string())
                print("sent -> " + row[2])
                # Append a new line to the success log file with the index and email address
                success_log.write(f"{i}: sent -> {row[0] + ' ' + row[2]}\n")
                email_count += 1  # Increment email count

            except Exception as e:
                print(f"failed -> {row[2]} {str(e)}")
                # Append a new line to the failure log file with the index, email address, and error
                failure_log.write(f"{i}: failed -> {row[0] + ' ' + row[2]} {str(e)}\n")

# Print the total number of emails sent
print(f"Total emails sent: {email_count}")

# Close the SMTP server
server.quit()
