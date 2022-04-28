import smtplib

import Constants as keys


class Mail:
    def __init__(self, recipient, subject, body):
        self.sender = keys.MAIL_EMAIL
        self.recipient = recipient
        self.subject = subject
        self.body = body

        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(self.sender, keys.MAIL_PASSWORD)

    def sendMail(self):
        message = f"Subject: {self.subject}\n\n{self.body}"
        self.server.sendmail(self.sender, self.recipient, message)
        print("Sending mail to {}...".format(self.recipient))
        print("From: {}".format(self.sender))
        print("Subject: {}".format(self.subject))
        print("Body: {}".format(self.body))
        print("")