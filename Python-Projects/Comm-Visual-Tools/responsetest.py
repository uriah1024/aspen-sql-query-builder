#!/usr/bin/env python3
import re
import ssl
import time
from os.path import abspath

import logging
from logging.config import dictConfig

import pymsteams
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Constants
USERNAME = '[username]'
PASSWORD = '[password]'

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename="site_info.log", 
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')
with open(abspath('/Users/[USER]/Desktop/hostedurl.txt')) as urls:
    file = open('site_data.txt', 'w+')
    try:
        for line in urls:
            url = line.rstrip('\n')
            aboutpage = url.replace('logon','about')
            homepage = url.replace('logon','home')
            initialRequest = requests.head(url)
            # If we have a good status, move to a login check.
            if initialRequest.status_code == 200:
                # Use 'with' to ensure the session context is closed after use.
                with requests.Session() as session:
                    # Fill in your details here to be posted to the login form.
                    payload = {
                        'username': USERNAME,
                        'password': PASSWORD
                    }
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'}
                    site = session.post(url, data=payload, headers=headers)

                    # Open session in browser to confirm successful login.
                    # This section is commented out. Only use this for debugging and with a 
                    # single URL in your file, unless you want to open 145 tabs in your browser.
                    
                    driver = webdriver.Firefox()
                    driver.get(url)

                    user = driver.find_element_by_name('username')
                    user.send_keys(USERNAME)
                    pw = driver.find_element_by_name('password')
                    pw.send_keys(PASSWORD)
                    pw.send_keys(Keys.RETURN)
                    time.sleep(3)
                    driver.get(aboutpage)
                    
                    # print the html returned or something more intelligent to see if it's 
                    # a successful login page.
                    # print(driver.page_source)
                    
                    # parse the html from the about page so that we can harvest site info
                    versionText = re.compile(r'Version ([^@]+\.[^@]+\.[^@]+\.[^@]+)', re.MULTILINE | re.DOTALL)
                    patchText = re.compile(r'Patch [a-zA-Z]', re.MULTILINE | re.DOTALL)
                    server = re.compile(r'.*\.follett.com$', re.MULTILINE | re.DOTALL)
                    soup = BeautifulSoup(driver.page_source, 'html.parser') # Parse the HTML

                    patch = ""
                    cluster = ""
                    data = soup.find('table')
                    for td in data.findAll('td'):
                        if versionText.match(td.text):
                            version = td.text
                        if patchText.match(td.text):
                            patch = td.text
                        if server.match(td.text):
                            cluster = td.text

                    # gracefully close down the pages we generate from this tool
                    driver.quit()
                    
                    # See how long the request takes, and convert to ms
                    elapsed_time = initialRequest.elapsed.microseconds / 1000
                    # The below line is performed to trim the results to seconds. Zero
                    # is everything before the decimal. One would be for everything after.
                    elapsed_ms = str(elapsed_time).split('.',1)[0]

            # If we don't return a healthy 200 code, we want to inform the team of that.
            # Therefore, we'll send a message to our MS Teams channel when something else
            # happens. The core of this process is to include a connectorcard, message, and
            # then to send the message.
            else:
                # Microsoft Webhook URL // This is the Tier 2 channel
                myTeamsMessage = pymsteams.connectorcard("[HTTPS WEBHOOK produced by MS Teams]")
                # Additional Channel URL // This one is Tech Support general chat
                myTeamsMessage.newhookurl('[HTTPS WEBHOOK produced by MS Teams]')
                # Title of message.
                title = 'ALERT for ('
                title += url
                title += ')'
                myTeamsMessage.title(title)
                pymsteams
                # Text to message.
                myTeamsMessage.text('Connection failed - Please review the site to ascertain the issue')
                # create the section
                myMessageSection = pymsteams.cardsection()
                # Activity Elements
                myMessageSection.activityTitle(' '.join('HTTP', initialRequest.status_code))
                myMessageSection.activitySubtitle("Code details can be found here: https://goo.gl/qb5n4v")
                myMessageSection.activityImage("https://www.clipartmax.com/png/middle/43-430549_science-lab-safety-symbols-clip-art-ionizing-radiation-symbol.png")
                myMessageSection.activityText("Please verify all nodes. 4xx errors are considered client side. 5xx errors are server side.")
                # Section Text
                myMessageSection.text("Node Template: http://[server name].fss.follett.com:8080/aspen/logon.do?deploymentId=[deployment id]")
                # Facts are key value pairs displayed in a list.
                myMessageSection.addFact("Status:      ", initialRequest.status_code)
                myMessageSection.addFact("Latency (ms):", str(elapsed_ms))

                # Section Images
                #myMessageSection.addImage("http://i.imgur.com/c4jt321l.png", ititle="This Is Fine")

                # Add your section to the connector card object before sending
                myTeamsMessage.addSection(myMessageSection)
                # Button for message
                myTeamsMessage.addLinkButton('Go to website', url)
                # Send the message.
                myTeamsMessage.send()

            # In Python, we have to assemble our strings with more effort. There's no 
            # StringBuilder like in Java.
            url_status = " status: ".join((url, str(initialRequest.status_code)))
            output = " latency (ms): ".join((url_status, str(elapsed_ms)))

            deploymentId = aboutpage.split('//', 1)
            deploymentId = deploymentId[1].split('/about.do')[0]
            if patch == "":
                file.write('{}, {}, {}\n'.format(output, version, cluster))
            else:
                file.write('{}, {} {}, {}\n'.format(output, version, patch, cluster))
            logging.info(output)
            print(output)
    except ConnectionError as conn:
        logging.error('Failed to connect: ')
        logging.error(conn)
        print("failed to connect")
    except ssl.CertificateError as cert:
        logging.error('Certificate Error: ')
        logging.error(cert)
        print('Certificate Error')
    else:
        logging.info('Program complete')
        print('program complete')
    file.close()
urls.close()
