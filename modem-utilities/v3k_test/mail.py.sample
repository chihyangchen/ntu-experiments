#!/usr/bin/python3

from email.message import EmailMessage
import mimetypes
import smtplib
import subprocess
import sys
# python3 mail.py  DEVICE_NAME  REASON(1-x)  [Attached file]
# REASON: 0: Regular report, 1: Loss connection, 2: SIM error, 3. GPIO toggling, 4: Thermal too High 

gmail_user = "chihyangchen0@gmail.com"
gmail_app_password = "xxxx"

sender = 'chihyangchen0@gmail.com'
#receivers = ['chihyang78@gmail.com']
receivers = [who]

REASON = ""
DEV = ""

if len(sys.argv) > 1:
    DEV = sys.argv[1]
if len(sys.argv) > 2:
    if sys.argv[2] == "1":
        REASON = " Loss connection: "
    elif sys.argv[2] == "2":
        REASON = " Flight Mode Toggling: "
    elif sys.argv[2] == "3":
        REASON = " Pwr GPIO Toggling: "
    elif sys.argv[2] == "4":
        REASON = " SIM ERROR: "
    elif sys.argv[2] == "5":
        REASON = " Thermal alarm: "
    elif sys.argv[2] == "6":
        REASON = " Re-dial failed: "
    else:
        REASON = " Normal send: "


email = EmailMessage()
email["From"] = sender #"chihyangchen0@gmail.com"
email["To"] = receivers #'chihyang78@gmail.com'
email["Subject"] = "Taoyuan Metro PoC -" + DEV

proc = subprocess.Popen(['date', '+%Y-%m-%d_%H-%M-%S'],stdout=subprocess.PIPE, shell=True)
(time,err) = proc.communicate()
current_time=time.decode("UTF-8")
#print(current_time)
body ="""

""" + REASON + """
""" + current_time

email.set_content(body)


if len(sys.argv) > 3:
    file_in = sys.argv[3]
	with open(file_in, 'rb') as file:
		email.add_attachment(file.read(), maintype='text', subtype='plain', filename=file_in)


try:
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465,timeout=10)

	server.login(gmail_user, gmail_app_password)
	server.send_message(email)
	server.quit()
	print("mail sent!")
except Exception as exception:
	print("Error: %s"  % exception)
	exit(1)






