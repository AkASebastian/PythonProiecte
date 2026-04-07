import string
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
from hashlib import new
import smtplib
sender='data_scraping@coneasorin.ro'
subject='Pretul a scazut la:'
to_addr_list = ['noul.witzkhalifa@gmail.com']
cc_addr_list = ['']
def sendemail(sender,message, subject,to_addr_list, cc_addr_list=[]):
    try:
        smtpserver='mail.x-it.ro:26'
        header  = 'From: %s\n' % sender
        header += 'To: %s\n' % ','.join(to_addr_list)
        header += 'Cc: %s\n' % ','.join(cc_addr_list)
        header += 'Subject: %s\n\n' % subject
        message = header + message
 
        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(sender,"stiinte217_2022")
        problems = server.sendmail(sender, to_addr_list, message)
        server.quit()
        return True
    except:
        return False
 
 
def data_scraping ():
    req=requests.get("https://www.emag.ro/telefon-mobil-apple-iphone-14-pro-max-128gb-5g-deep-purple-mq9t3rx-a/pd/DXDY4LMBM/?X-Search-Id=50b61f5c4394ddee13da&X-Product-Id=101075766&X-Search-Page=1&X-Search-Position=2&X-Section=search&X-MB=0&X-Search-Action=view")
    soup=BeautifulSoup(req.text,"html.parser")
    price=soup.find('p', attrs={'class': 'product-new-price'}).text
    new_price=price[0:5]
    new_price=new_price.replace(".","")
    new_price=int(new_price)
    pret_referinta = 7079
    if(new_price<pret_referinta):
        sendemail(sender,"Pretul a scazut" , subject,to_addr_list, cc_addr_list=[])
        print("Pretul a scazut")
    else:
        print("pretul a crescut")
#data_scraping()        
 
 
 
 
#def trimitere_email ():
    # server = smtplib.SMTP('mail.x-it.ro',26)
  #  server.starttls()
   # server.login("data_scraping@coneasorin.ro", "stiinte217_2022")
   # server.sendmail("data_scraping@coneasorin.ro","noul.witzkhalifa@gmail.com", "UPDATE: AVEM O MODIFICARE DE PRET")
  #  print("Emailul a fost trimis cu succes")
   # server.quit
 
#data_scraping()
#trimitere_email()
sendemail(sender,"Pretul a scazut" , subject,to_addr_list, cc_addr_list=[])
