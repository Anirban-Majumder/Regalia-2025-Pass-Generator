from unicodedata import name
from pandas import read_csv
from PIL import Image, ImageDraw, ImageFont
import pyqrcode
import json

def load_font(font_path, font_size):
    try:
        return ImageFont.truetype(font_path, font_size)
    except OSError:
        print(f"Error: Font file '{font_path}' not found.")
        return None

def makeCertificate(student, template, detailsFont, allowedFont):
    cert = template.copy()
    draw = ImageDraw.Draw(cert)
    
    # Split student data
    student_info = student[0].split('\t')
      
    student_data = {
        "name": student_info[0],
        "phone": student_info[1],
        "email": student_info[2],
        "roll": student_info[3]
    }
    
    # Generate QR code
    qr_data = json.dumps(student_data)
    qr_size = makeQR(qr_data)
    qr_pos = ((842 - int(qr_size / 2)), 160)
    cert.paste(Image.open('qr_code.png'), qr_pos)
    
    # Calculate name font size
   # Calculate name font size
nameFont = 150
font = ImageFont.truetype("Poppins-Bold.ttf", nameFont)
name_width, _ = font.getsize(student_info[0].upper())
difference = name_width - (1682 - 440)
if 0 < difference <= 100:
    nameFont = 130
elif 100 < difference <= 250:
    nameFont = 110
elif 250 < difference <= 400:
    nameFont = 100
elif difference > 400:
    nameFont = 80
else:
    nameFont = 150

    
    # Draw name, email, and roll
    draw.text(xy=(220, 1450), text=student_info[0].upper(), fill='white', font=ImageFont.truetype("Poppins-Bold.ttf", nameFont))
    draw.text(xy=(220, 1650), text=student_info[2], fill='white', font=detailsFont)
    draw.text(xy=(220, 1740), text=student_info[3].upper(), fill='white', font=detailsFont)
    
    # Save certificate
    cert_path = f"img/{student_info[0]}_pass.png"
    cert.save(cert_path)
    print(f"Certificate saved: {cert_path}")

def makeQR(data):
    qr = pyqrcode.create(data)
    qr.png('qr_code.png', scale=30, module_color='#03045E', background='#538EFF')
    return qr.get_png_size(30)

try:
    data = read_csv("data.csv").values.tolist()
    template = Image.open("pass_template.png")
    detailsFont = load_font("Poppins-Regular.ttf", 60)
    allowedFont = load_font("Poppins-SemiBold.ttf", 65)

    if detailsFont is None or allowedFont is None:
        raise RuntimeError("Font loading failed.")

    for student in data:
        makeCertificate(student, template, detailsFont, allowedFont)

except FileNotFoundError:
    print("Error: CSV file or template image not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
