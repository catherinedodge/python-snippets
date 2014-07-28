# Written at the 2013 DC Lady Hackathon for Karen

import email, getpass, imaplib, os
import smtplib
from email.mime.text import MIMEText

user = raw_input("Enter your GMail username:")
pwd = getpass.getpass("Enter your password: ")

# connecting to the gmail imap server
m = imaplib.IMAP4_SSL("imap.gmail.com")
m.login(user,pwd)
m.select("INBOX") 

# here you a can choose a mail box like INBOX instead
# use m.list() to get all the mailboxes

resp, items = m.search(None, 'SUBJECT', '"Re: A Quote to Share, and other things"')

# you could filter using the IMAP rules here 
# (check http://www.example-code.com/csharp/imap-search-critera.asp)
# resp is response code from server. it prints "Ok"

items = items[0].split() # getting the mails id

for emailid in items:
    resp, data = m.fetch(emailid, "(RFC822)") 
# fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
    email_body = data[0][1] # getting the mail content
    mail = email.message_from_string(email_body) 

    # we use walk to create a generator so we can iterate on the parts 
    # and forget about the recursive headache
    for part in mail.walk():
        # multipart are just containers, so we skip them
        if part.get_content_type() == 'text/plain':
            fullmsg=part.get_payload()
            qs=0
            for (counter,line) in enumerate(fullmsg):
               if line == "<":
                    qs=counter
                    break
            text=fullmsg[0:qs]
            index_of_colon = text.rfind(":", 0, qs)
            quote = text[0:index_of_colon-25]
            msg=MIMEText(quote)
            msg['Subject']=mail["From"]
            msg['From'] = 'xxx@gmail.com'
            msg['To'] = 'xxx@post.wordpress.com'
            s = smtplib.SMTP('smtp.gmail.com')
            server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user,pwd)
            server.sendmail('xxx@gmail.com','xxx@post.wordpress.com',msg.as_string())
    server.close()            
