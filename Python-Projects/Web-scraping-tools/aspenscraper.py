import cookiejar
import re
import ssl
import time
import urllib.request
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.TimeoutError)
from os.path import abspath

import mechanize
from robobrowser import RoboBrowser
import requests
from getpass import getpass
from bs4 import BeautifulSoup
from selenium import webdriver

# Constants
USERNAME = 'aspensupport'
PASSWORD = '!RC8T3W2$'

# Fetch our URL file
with open(abspath('/Users/[USER]/Desktop/aspen_url.txt')) as urls:

# Loop through URLs to fetch the version info from each site.
# 10-8-2019 - Login to capture the cluster data.
# 10-8-2019 - Capture page response times.
# Capture exceptions, so that we don't halt.
# Save the output to a file so we can move our data to Pando.
    # file = open('version_data.txt', 'w+')
    for line in urls:
        url = line.rstrip('\n') # Remove spaces between URLs
        aboutpage = url.replace('logon','about')
        referUrl = url.replace('logon','home')
        try:
            status = requests.get(url, verify=False, timeout=(2, 5)) # Check the status of the url
            data = {
                'username': USERNAME,
                'password': PASSWORD,
                'userEvent': 930,
                'formFocusField': 'username',
                'mobile': 'false'
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
            }
            #with requests.Session() as session:
                #session.auth = (USERNAME, PASSWORD)
                #obtain CSRF cookie
                #initial_response = session.get(url, verify=False, timeout=(2, 5))
                #print(session.cookies.get_dict())
                # payload['csrf_test_name'] = session.cookies['org.apache.struts.taglib.html.TOKEN']
                # Now actually post with the correct CSRF cookie
                #response = session.post(url, data=data, json=None, headers=headers)
                #about = session.get(aboutpage, verify=False, timeout=(2, 5))
                #print(session.headers)
                #print(session.cookies)
                #print(about.text)

            # mechanize code
            #browser = mechanize.Browser()
            #browser.open(url)
            #browser.form = list(browser.forms())[0]
            #browser.form['username'] = USERNAME
            #browser.form['password'] = PASSWORD
            #print("TEST")
            #browser.submit()
            #about = browser.open(aboutpage)
            #returnabout = about.read()
            #print(returnabout)
            # end mechanize

            # Robobrowser code
            # browser = RoboBrowser(history=True, parser="html.parser")
            # browser.open(url)
            # form = browser.get_form()
            # form
            # form['username'].value = USERNAME
            # form['password'].value = PASSWORD
            # browser.session.headers['Referer'] = url
            # user = form['username'].value
            # print(user)
            # pw = form['password'].value
            # print(pw)

            # browser.submit_form(form)
            # browser.open(aboutpage)
            # print(browser.parsed)
            # End Robobrowser

            # Selenium

            # End Selenium

            # Grab deployment ID for output later. This allows us to match in Pando.
            deploymentId = aboutpage.split('//', 1)
            deploymentId = deploymentId[1].split('/about.do')[0]
            if status.status_code == 200:
                versionText = re.compile(r'Version ([^@]+\.[^@]+\.[^@]+\.[^@]+)', re.MULTILINE | re.DOTALL)
                patchText = re.compile(r'Patch [a-zA-Z]', re.MULTILINE | re.DOTALL)
                server = re.compile(r'[a-zA-Z].follett.com', re.MULTILINE | re.DOTALL)
                soup = BeautifulSoup(aboutpage.text, 'html.parser') # Parse the HTML

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
                # file.write('{}, {} {}\n'.format(deploymentId, version, patch))
                print('{}, {} {} {}'.format(deploymentId, version, patch, cluster))
                time.sleep(0.5) #Don't get flagged as a bot or crash the servers
            else:
                print("Message: {}, {}".format(deploymentId, status))
        except requests.exceptions.ConnectionError as h:
            print(h)
            continue
        except requests.exceptions.RequestException as e:
            print(e)
            continue
        except Exception as x:
            print(x)

    # file.close()
urls.close()
