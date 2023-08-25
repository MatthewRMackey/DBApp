import sys
import socket

import qrcode
from qrcode.image.styledpil import StyledPilImage

def generateQR(link, name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    local_ip = sock.getsockname()[0]
    phrase = "http://"+local_ip+":5000/item_page/"+str(link)
    qr = qrcode.QRCode(version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4)
    qr.add_data(phrase)

    img = qr.make_image(image_factory=StyledPilImage, fit=True)
    img.save("../flaskr/static/img/"+name+".png")