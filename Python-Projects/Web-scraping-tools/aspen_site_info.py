#!/usr/bin/env python3
# import cProfile
import re
import ssl
import time
from os.path import abspath

import logging
from logging.config import dictConfig

import getpass
import pymsteams
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options

# exe file generation requirement - this goes in the spec file. It's referenced here only as a guide.
# import sys
# sys.setrecursionlimit(5000)

# Constants
USERNAME = '[username]'
PASSWORD = getpass.getpass()

class aspen_site_info():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        filename="site_info.log",
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    startMsg = ("\n\n*****ASPEN SITE INFO*****\n\n"
                "Thank you for running Aspen Site Info!\n"
                "This tool was written by JM from Technical Support. If you discover an issue, please report it to jm---@---.com\n\n"
                "This tool produces 2 files:\n "
                "1) site_data.txt, which collects the Aspen version, patch, and cluster info.\n "
                "2) site_info.log, which collects the site name and the HTTP status of the site and the latency at the time of the check.\n\n")
    print(startMsg)
    with open(abspath('/Users/[USER]/Desktop/hostedurl.txt')) as urls:
        file = open('site_data.txt', 'w+')
        try:
            for line in urls:
                url = line.rstrip('\n')
                aboutpage = url.replace('logon', 'about')
                logout = url.replace('logon', 'logout')
                deploymentId = aboutpage.split('//', 1)
                deploymentId = deploymentId[1].split('.')[0]
                initialRequest = requests.head(url)
                # If we have a good status, move to a login check.
                if initialRequest.status_code == 200:
                    # Selenium is necessary to login to Aspen for this project. I was not able to mimic
                    # the javascript 'this.form.submit' function through Response alone. That could be
                    # personal limitation.
                    options = Options()
                    options.add_argument('-headless')
                    driver = Firefox(executable_path='geckodriver', options=options)
                    wait = WebDriverWait(driver, timeout=3)
                    driver.get(url)

                    driver.find_element_by_name('username').send_keys(USERNAME)
                    pw = driver.find_element_by_name('password')
                    pw.send_keys(PASSWORD)
                    pw.send_keys(Keys.RETURN)
                    # implicitly wait up to 10 sec for the page to load after logging in. Once done, we can move on.
                    wait.until(lambda x: x.find_element_by_id("contextMenu"))
                    #time.sleep(.3)
                    driver.get(aboutpage)

                    # parse the html from the about page so that we can harvest site info
                    versionText = re.compile(
                        r'Version ([^@]+\.[^@]+\.[^@]+\.[^@]+)', re.MULTILINE | re.DOTALL)
                    patchText = re.compile(
                        r'Patch [a-zA-Z]', re.MULTILINE | re.DOTALL)
                    server = re.compile(r'.*\.follett.com$',
                                        re.MULTILINE | re.DOTALL)
                    soup = BeautifulSoup(
                        driver.page_source, 'html.parser')  # Parse the HTML

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

                    # We want to end the Aspen user session we generate. Navigating to the logout screen should natively do this.
                    #element = WebDriverWait(driver, 10).until(
                    #    lambda x: x.find_element_by_xpath("//*[@id='popupWindow']/tbody/tr[2]/td/table/tbody/tr[6]/td"))
                    driver.get(logout)
                    # gracefully close down the pages we generate from this tool
                    driver.quit()

                    # See how long the request takes, and convert to ms
                    elapsed_time = initialRequest.elapsed.microseconds / 1000
                    # The below line is performed to trim the results to seconds. Zero
                    # is everything before the decimal. One would be for everything after.
                    elapsed_ms = str(elapsed_time).split('.', 1)[0]

                # If we don't return a healthy 200 code, we want to inform the team of that.
                # Therefore, we'll send a message to our MS Teams channel when something else
                # happens. The core of this process is to include a connectorcard, message, and
                # then to send the message.
                else:
                    # Microsoft Webhook URL // This is the Tier 2 channel
                    myTeamsMessage = pymsteams.connectorcard(
                        "[HTTPS WEBHOOK produced by MS Teams]")
                    # Additional Channel URL // This one is Tech Support general chat
                    myTeamsMessage.newhookurl(
                        '[HTTPS WEBHOOK produced by MS Teams]')
                    # Title of message.
                    title = 'ALERT for ('
                    title += url
                    title += ')'
                    myTeamsMessage.title(title)
                    pymsteams
                    # Text to message.
                    myTeamsMessage.text(
                        'Connection failed - Please review the site to ascertain the issue')
                    # create the section
                    myMessageSection = pymsteams.cardsection()
                    # Activity Elements
                    myMessageSection.activityTitle(
                        ' '.join('HTTP', initialRequest.status_code))
                    myMessageSection.activitySubtitle(
                        "Code details can be found here: https://goo.gl/qb5n4v")
                    myMessageSection.activityImage(
                        "https://www.clipartmax.com/png/middle/43-430549_science-lab-safety-symbols-clip-art-ionizing-radiation-symbol.png")
                    myMessageSection.activityText(
                        "Please verify all nodes. 4xx errors are considered client side. 5xx errors are server side.")
                    # Section Text
                    myMessageSection.text(
                        "Node Template: http://[server_name_here].fss.follett.com:8080/aspen/logon.do?deploymentId=[{deploymentId}]")
                    # Facts are key value pairs displayed in a list.
                    myMessageSection.addFact(
                        "Status:      ", initialRequest.status_code)
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
                url_status = " status: ".join(
                    (url, str(initialRequest.status_code)))
                output = " latency (ms): ".join((url_status, str(elapsed_ms)))

                if patch == "":
                    file.write('{}, {}, {}\n'.format(output, version, cluster))
                else:
                    file.write('{}, {} {}, {}\n'.format(
                        output, version, patch, cluster))
                logging.info(output)
                print(deploymentId)
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
#cProfile.run('aspen_site_info()', sort = 'tottime')