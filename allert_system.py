import smtplib


def send_Email(message, receiver, SUBJECT="STOCK MARKET PATTERN ALLERT"):
    sender ='stcstockmarketallert@gmail.com'
    password = "12345678STC@5"
    #sender = "suntradingbotalert@gmail.com"
    #password = "JesusistheLord@5"
    email = ' '.join([str(elem) for elem in message])
    email = 'Subject: {}\n\n{}'.format(SUBJECT, email)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    print("Login success: ",SUBJECT)
    #
    for i in receiver:
        server.sendmail(sender, i, email)
    print('Email Sent')


