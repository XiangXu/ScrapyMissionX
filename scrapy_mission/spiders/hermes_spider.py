import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scrapy.utils.project import get_project_settings
import scrapy

settings=get_project_settings()
# diable scrapy log
logging.getLogger('scrapy').propagate = False
logger = logging.getLogger('hermes_spider_logger')

class HermesSpider(scrapy.Spider):
    name = "hermes"

    def start_requests(self):
        urls = [
            'https://www.hermes.com/ie/en/search/?s=herbag#||Category',
            'https://www.hermes.com/ie/en/search/?s=picotin#||Category',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.logger.info('Parse function called on %s', response.url)
        response_str = response.text
        if 'class="main-title"' in response_str:
            search_result_str = self.find_between(response_str, 'class="main-title">','</div>')
            if 'Oops!' in search_result_str:
                self.logger.info('Did not find anything, existing')
            else:
                item_name = self.find_between(response_str, 'Here are the results for “','”</span>')
                item_number = self.find_between(response_str, 'aria-hidden="true"> (', ') </span>')
                self.send_result_found_message(item_name, item_number)
        else:
            self.logger.info('No main title found, existing')
            
    def send_result_found_message(self, item_name, item_number):
        self.emailHandler('Item name: %s\nItem number: %s ' % (item_name, item_number))

    def emailHandler(self, email_body):
        gmailUser = settings.get('GMAIL_USERNAME')
        gmailPassword = settings.get('GMAIL_PASSWORD')
        recipient = settings.get('GMAIL_RECIPIENT')
        msg = MIMEMultipart()
        msg['From'] = gmailUser
        msg['To'] = recipient
        msg['Subject'] = "Hermes search result"
        msg.attach(MIMEText(email_body))

        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.login(gmailUser, gmailPassword)
        mailServer.sendmail(gmailUser, recipient, msg.as_string())
        mailServer.close()
        
        self.logger.info('Email sent with message %s', email_body)

    def find_between(self, s, first, last):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""