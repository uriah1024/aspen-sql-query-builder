#!/usr/bin/env python3
import ssl
from os.path import abspath

import logging
from logging.config import dictConfig

import pyshark
import pymsteams
import requests
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Produces a log text file that contains the necessary info formatted for technical teams.
# --- LOG OUTPUT EXAMPLE ---
# 2018-12-27 15:04:46 INFO     https://site-url status: 200 latency (ms): 48
# 2018-12-27 15:04:46 INFO     Program complete
# --- END EXAMPLE ---
# If we have a reason to report a website to the tech teams, we do so using MS Teams.
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename="uptimeLog.log", 
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')
with open(abspath('/Users/[USER]/Desktop/hostedurl.txt')) as urls:

    try:
        for line in urls:
            url = line.rstrip('\n')
            # Collect packet data for traffic analysis.
            capture = pyshark.LiveCapture(interface='Local Area Connection', bpf_filter='ip and tcp')
            def print_conversation_header(packet):
                try:
                    protocol =  packet.transport_layer
                    src_addr = packet.ip.src
                    src_port = packet[packet.transport_layer].srcport
                    dst_addr = packet.ip.dst
                    dst_port = packet[packet.transport_layer].dstport
                    print(f'[Protocol]: {protocol}   [Source]: {src_addr}:{src_port} --> [Destination]: {dst_addr}:{dst_port}')
                except AttributeError as e:
                    print(e)
                    #ignore packets that aren't TCP/UDP or IPv4
                    pass
            #capture.apply_on_packets(print_conversation_header, timeout=60, packet_count=6)
            capture.sniff(packet_count=6, timeout=60)
            initialRequest = requests.head(url)
            #print(capture)
            for packet in capture:
                print_conversation_header(packet)
                #print(dir(packet[0]))
                print(packet.pretty_print())
                #print("[Protocol:] "+packet.highest_layer+" [Source IP:] "+packet['ip'].src+" [Destination IP:]"+packet['ip'].dst)
                #continue
                #print(f'This packet: {packet}')
            # If we have a good status, move to a login check.
            if initialRequest.status_code == 200:
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
                ats = []
                ats.append('HTTP ')
                ats.append(str(initialRequest.status_code))
                ats2 = ''.join(ats)
                
                myMessageSection.activityTitle(ats2)
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
urls.close()