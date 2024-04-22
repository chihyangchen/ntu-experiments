from email.message import EmailMessage
import mimetypes
import smtplib
import subprocess
import sys


gmail_user = "chihyangchen0@gmail.com"
gmail_app_password = "xxxxxxxxxxxxxxxxxxxxx"

sender = 'chihyangchen0@gmail.com'
receivers = ['chihyang78@gmail.com']

reason = ""
dev = ""

if len(sys.argv) > 1:
    dev = sys.argv[1]
if len(sys.argv) > 2:
    if sys.argv[2] == "0":
        reason = " Regular report: "
    elif sys.argv[2] == "1":
        reason = " Loss connection: "
    elif sys.argv[2] == "2":
        reason = " SIM error: "
    else:
        reason = " Just to send: "


email = EmailMessage()
email["From"] = sender #"chihyangchen0@gmail.com"
email["To"] = receivers #'chihyang78@gmail.com'
email["Subject"] = "Taoyuan Metro PoC -" + dev

proc = subprocess.Popen(['date', '+%Y-%m-%d_%H-%M-%S'],stdout=subprocess.PIPE, shell=True)
(time,err) = proc.communicate()
current_time=time.decode("UTF-8")
#print(current_time)
body ="""

""" + reason + """
""" + current_time

email.set_content(body)


if len(sys.argv) > 3:
    file_in = sys.argv[3]
	with open(file_in, 'rb') as file:
		email.add_attachment(file.read(), maintype='text', subtype='plain', filename=file_in)


try:
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

	server.login(gmail_user, gmail_app_password)
	server.send_message(email)
	server.quit()
	print("mail sent!")
except Exception as exception:
	print("Error: %s"  % exception)
	exit(1)






