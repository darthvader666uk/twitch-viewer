'''
Copyright 2015 ohyou
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import requests
import subprocess
import json
import sys
import multiprocessing
import time
import random
import argparse
import logging
import os
from lxml.html import fromstring
from datetime import datetime, timedelta

def get_channel(args):
    global user
    global clientid
    global processes
    global noOfProxies
    clientid = sys.argv[1]
    user = sys.argv[2]
    noOfProxies = int(sys.argv[3])
    #Make sure it isnt greater than 20 as https://free-proxy-list.net/uk-proxy.html only displays 20
    if noOfProxies > 20:
        noOfProxies = 20
    processes = []

def get_proxies():
    url = 'https://free-proxy-list.net/uk-proxy.html'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:noOfProxies]:
        if i.xpath('.//td[3][contains(text(),"GB")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
            #Check if Proxies are empty
            if not proxies:
                proxies = ['46.101.1.221:80', '68.183.220.18:80', '206.189.205.65:80']
    return proxies

def get_url():
    try:
        if os.name == 'nt':
            response = subprocess.Popen(["streamlink", "--http-header", "Client-ID="+clientid, "https://twitch.tv/"+user, "-j"], stdout=subprocess.PIPE).communicate()[0]
        else:
            response = subprocess.Popen(["/home/darthvader666uk/.local/bin/streamlink", "--http-header", "Client-ID="+clientid, "https://twitch.tv/"+user, "-j"], stdout=subprocess.PIPE).communicate()[0]
    except subprocess.CalledProcessError:
        print ("1 - An error has occurred while trying to get the stream data. Is the channel online? Is the channel name correct?")
        sys.exit(1)
    except OSError:
        print ("An error has occurred while trying to use streamlink package. Is it installed? Do you have Python in your PATH variable?")
    try:
        url = json.loads(response)['streams']['worst']['url']
    except:
        try:
            url = json.loads(response)['streams']['audio_only']['url']
        except (ValueError, KeyError):
            print ("2 - An error has occurred while trying to get the stream data. Is the channel online? Is the channel name correct?")
            print(response)
            sys.exit(1)
 
    return url


def open_url(url, proxy, clientid, user):
    # Sending HEAD requests
    while True:
        try:
            with requests.Session() as s:
                response = s.head(url, proxies=proxy)
            print("Sent HEAD request with %s" % proxy["http"])
            print(response)
            time.sleep(5)
            check_viewers = get_viewers(clientid, user)
            print(check_viewers)
            time.sleep(5)
        except requests.exceptions.Timeout:
            print("  Timeout error for %s" % proxy["http"])
        except requests.exceptions.ConnectionError:
            print("  Connection error for %s" % proxy["http"])
            print("  Refreshing Proxies ...")
            prepare_processes()


def prepare_processes():
    global processes
    proxies = get_proxies()
    print(proxies)
    n = 0

    if len(proxies) < 1:
        print("An error has occurred while preparing the process: Not enough proxy servers. Need at least 1 to function.")
        sys.exit(1)

    for proxy in proxies:
        # Preparing the process and giving it its own proxy
        processes.append(
            multiprocessing.Process(
                target=open_url, kwargs={
                    "url": get_url(), "proxy": {
                        "http": proxy
                    }, "clientid" :clientid, "user" : user
                }
            )
        )
        print('Preparing View Bot: %s' %n),
        n += 1
    print('')

# THis Section is for logging and checking view count
def get_viewers(clientid, user):
    url = "https://api.twitch.tv/kraken/streams/"+user+"?client_id="+clientid
    # print(url)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("API returned {0}".format(r.status_code))
    infos = r.json()
    stream = infos['stream']
    results = {}
    stream_results = {}
    if not stream:
        results = {'online':False,'title':None,'viewers':0}
        stream_results['Status'] = "Offline"
        stream_results['Viewers'] = 0
    else:
        viewers = stream['viewers']
        title = stream['channel']['status']
        stream_results['Status'] = "Online"
        stream_results['Viewers'] = viewers
        results = {'online':True,'title':title,'viewers':viewers}

    results['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    results['stream'] = user
    return stream_results
# End Logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Twitch Bot')
    parser.add_argument('clientid', help='CLient ID -- Need to make an App in Twitch Developers: https://glass.twitch.tv/console/apps')
    parser.add_argument('user', help='Twitch Username')
    parser.add_argument('noOfProxies', help='Specify No. of Proxies. Max 20')
    parser.add_argument('maxViewBotTime', help='Set a View Bt timeout to stop twitch views', action='store_true')
    args = parser.parse_args()

    clientid = sys.argv[1]
    user = sys.argv[2]
    noOfProxies = int(sys.argv[3])

    #Check if there is a max time to kill the bot
    if sys.argv[4:]:
        maxViewBotTime = int(sys.argv[4])
    else:
        maxViewBotTime = 86400 #24 hours

    killTime = time.time()

    print("Obtaining the channel...")
    get_channel(args)
    print("Preparing the processes...")
    prepare_processes()
    print("Prepared the processes")
    print("Booting up the processes...")

    # Timer multiplier
    n = 8

    # Starting up the processes
    for process in processes:
        time.sleep(random.randint(1, 5) * n)
        process.daemon = True
        process.start()
        if n > 1:
            n -= 1

    # Running infinitely
    while True:
        time.sleep(1)

        #If a time is set, lets kill it once times up - 300 = 5mins
        if maxViewBotTime:
            if time.time() > killTime + maxViewBotTime : 
                print("Viewbot has eneded.")
                print("Time is %s " % time.time())
                print("Start Time was %s " % killTime)
                print("Max View bot time was %s " % maxViewBotTime)
                break