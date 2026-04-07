#!/usr/bin/env python3
# import cProfile
import logging
import re
import ssl
import time
from datetime import date
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from os.path import abspath

import pymsteams
import requests
import yaml
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# exe file generation requirement - this goes in the 'spec' file. It's referenced here only as a guide.
# import sys
# sys.setrecursionlimit(5000)

# Get inputs from config file
with open('R:/Tech Support/Aspen/python/live_files/cps_sync_config.yml', 'r') as ymlconfig:
    cfg = yaml.load(ymlconfig)

# Constants
USERNAME            = cfg['login']['username']
PASSWORD            = cfg['login']['password']
fileStorage         = cfg['storage']['fileStorage']
loggingFile         = cfg['storage']['loggingFile']
prodNodeUrls        = cfg['storage']['prodNodeUrls']
testNodeUrls        = cfg['storage']['testNodeUrls']
screenshotStorage   = cfg['storage']['screenshotStorage']

# Variables
productionpeerlist = cfg['productionpeerlist']
uatpeerlist = cfg['uatpeerlist']

# Convert a string into a list
def ConvertString(string):
    li = list(string.split(' '))
    return li

# Get difference of two lists using set()
def Diff(li1, li2):
    return (list(set(li1) - set(li2)))

# custom expected condition
# utilizes regex for text to compare
class wait_for_text_to_match(object):
    def __init__(self, locator, regexp):
        self.locator = locator
        self.regexp = regexp

    def __call__(self, driver):
        element_text = EC._find_element(driver, self.locator).text
        return re.search(self.regexp, element_text)

# logging setup
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')
logFile = f'{fileStorage}/{loggingFile}'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=20, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('cps_sync')
app_log.addHandler(my_handler)
app_log.setLevel(logging.INFO)

# Run the program indefinitely
#while True:

# UAT file for testing: uat_cps_node_urls.txt
# PROD file for go-live: internal_cps_node_urls.txt
with open(f'{fileStorage}/{prodNodeUrls}') as urls:
    try:
        for line in urls:
            url = line.rstrip('\n')
            monitorpage = url.replace('logon', 'monitor')
            syncinfo = url.replace(
                'logon.do', 'pages/core/monitoring/syncInfo.jsp')
            logout = url.replace('logon', 'logout')
            # grab the deployment ID for Teams message, if needed.
            if url != '':
                deploymentId = url.split('//', 1)
                deploymentId = deploymentId[1].split('.')[0]
                port = url.split(':', 2)
                port = port[2].split('/')[0]
                cpsId = '{}:{}'.format(deploymentId, port)
                initialRequest = requests.head(url)
                # If we have a good status, move to a login check. If not, report this to the team.
                if initialRequest.status_code == 200:
                    print(f"Running for {cpsId}")
                    # Selenium is necessary to login to Aspen for this project. I was not able to mimic
                    # the javascript 'this.form.submit()' function through Response alone. That could be
                    # personal limitation.
                    options = Options()
                    options.add_argument('-headless')
                    driver = Firefox(
                        executable_path='geckodriver', options=options)
                    wait = WebDriverWait(driver, timeout=5)
                    driver.get(url)

                    driver.find_element_by_name('username').send_keys(USERNAME)
                    pw = driver.find_element_by_name('password')
                    pw.send_keys(PASSWORD)
                    pw.send_keys(Keys.RETURN)
                    # Wait for the page to load after logging in. Once done, we can move on.
                    wait.until(lambda x: x.find_element_by_id("contextMenu"))

                    # Navigate to monitor
                    try:
                        driver.set_page_load_timeout(5)
                        driver.get(monitorpage)
                        wait.until(lambda x: x.find_element_by_id("syncInfo"))
                        # Navigate to jsp to collect current node data. This has to be done as base page does not contain data.
                        driver.get(syncinfo)

                        # parse the html from the about page so that we can harvest site info
                        soup = BeautifulSoup(
                            driver.page_source, 'html.parser')  # Parse the HTML
                        # Get form data from this page. We want to log this info.
                        table = soup.find('table')
                        rows = table.findAll('tr')[1:10]
                        del rows[1:5]
                        for row in rows:
                            cols = row.findAll('td')
                            cols = [obj.text.strip() for obj in cols]
                            app_log.info(cols)

                        # Get the peers list
                        for td in table.findAll('td')[19:20]:
                            peers = ConvertString(td.text)
                            peers.remove('')
                        # Get the last sync time
                        for resync in table.findAll('td')[13:14]:
                            lastsync = resync.text

                        # empty strings are falsy. If the string would not be false, then print the difference.
                        if not Diff(peers, productionpeerlist):
                            print('Full match - no sync issue')
                            app_log.info('Full match - no sync issue')
                        # loop back to reinitialize and recheck the peer list.
                        else:
                            difference = Diff(peers, productionpeerlist)
                            app_log.info('Missing peers detected. See below. Reinitializing and rechecking peers.')
                            app_log.info(difference)
                            print(
                                'Missing peers detected. See below. Reinitializing and rechecking peers.\n')
                            print(difference)
                            driver.get(monitorpage)
                            wait.until(lambda x: x.find_element_by_id("syncInfo"))
                            reinit = driver.find_element_by_link_text(
                                'reinitialize')
                            if len(reinit) > 0:
                                reinit.click()
                            userEvent = monitorpage.replace(
                                'monitor.do', 'monitor.do?userEvent=2350')
                            driver.get(userEvent)
                            driver.get(syncinfo)
                            syncData = BeautifulSoup(
                                driver.page_source, 'html.parser')  # Parse the HTML
                            table = syncData.find('table')
                            rows = table.findAll('tr')[1:10]
                            del rows[1:5]
                            for row in rows:
                                cols = row.findAll('td')
                                cols = [obj.text.strip() for obj in cols]
                                app_log.info(cols)

                            for td in table.findAll('td')[19:20]:
                                updatedpeers = ConvertString(td.text)
                                updatedpeers.remove('')
                            if not Diff(peers, productionpeerlist):
                                app_log.info('Full match - no sync issue')
                                print('Full match - no sync issue')
                            # Second pass failed. Alert team to sync issue.
                            else:
                                secondDiff = Diff(peers, productionpeerlist)
                                ssFileName = cpsId.replace(':', '_')
                                ss = f'{screenshotStorage}/{ssFileName}.png'
                                driver.save_screenshot(ss)
                                app_log.info('Second pass for peers failed. See below. Alerting team to issue.')
                                app_log.info(secondDiff)
                                print(
                                    'Second pass for peers failed. See below. Alerting team to issue.\n')
                                print(secondDiff)

                                # MS Teams Code
                                # Microsoft Webhook URL // This goes to the CPS Performance channel in Aspen Enterprise Support
                                myTeamsMessage = pymsteams.connectorcard(
                                    '[HTTPS WEBHOOK produced by MS Teams]')
                                # Title of message.
                                title = 'ALERT for Node Instance '
                                title += cpsId
                                title += ''
                                myTeamsMessage.title(title)
                                pymsteams
                                # Text to message.
                                msmessage = 'A synchronization issue was detected from this node. The following peers were found to be missing: {}'.format(
                                    secondDiff)
                                myTeamsMessage.text(msmessage)
                                # create the section
                                myMessageSection = pymsteams.cardsection()
                                # Activity Elements
                                atitle = f'Last sync initialized: {lastsync}'
                                myMessageSection.activityTitle(atitle)
                                myMessageSection.activitySubtitle(
                                    "Node restarts may be required.")
                                myMessageSection.activityImage(
                                    "https://static.thenounproject.com/png/966838-200.png")
                                myMessageSection.activityText(
                                    "This node was resynchronized prior to sending this message. Please verify all nodes before involving OLS.")
                                # Section Text
                                myMessageSection.text(f"Node: {cpsId}")
                                # Facts are key value pairs displayed in a list.
                                # Add your section to the connector card object before sending
                                myTeamsMessage.addSection(myMessageSection)
                                myMessageSection.addFact('See screenshot', ss)
                                # Button for message
                                myTeamsMessage.addLinkButton('Go to website', url)
                                # Send the message.
                                myTeamsMessage.send()
                    except TimeoutException as tex:
                        app_log.error(f"Monitor timed out for {cpsId}")
                        app_log.error(tex)
                        print(f"Monitor timed out for {cpsId}")
                        # If we failed to load the monitor, we need to try and logout and close this instance.
                        driver.get(logout)
                        driver.close()
                        continue

                    # Aspen requires that we not leave a session on monitor.do, lest we flood logging.
                    # We want to end the session by logging out, which is automatic when using this url.
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
                    # Additional Channel URL // This goes to the CPS Performance channel in ASpen Enterprise Support
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
                        f'HTTP {initialRequest.status_code}')
                    myMessageSection.activitySubtitle(
                        "Code details can be found here: https://goo.gl/qb5n4v")
                    myMessageSection.activityImage(
                        "https://www.clipartmax.com/png/middle/43-430549_science-lab-safety-symbols-clip-art-ionizing-radiation-symbol.png")
                    myMessageSection.activityText(
                        "Please verify all nodes. 4xx errors are considered client side. 5xx errors are server side.")
                    # Section Text
                    myMessageSection.text(f"Node: {cpsId}")
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

            # logging.info(td_list)
            # print(td_list)
    except ConnectionError as conn:
        app_log.error('Failed to connect: ')
        app_log.error(conn)
        print("failed to connect")
    except ssl.CertificateError as cert:
        app_log.error('Certificate Error: ')
        app_log.error(cert)
        print('Certificate Error')
    else:
        app_log.info('Program complete')
        print('program complete')

urls.close()
