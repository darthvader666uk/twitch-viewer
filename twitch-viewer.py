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
from lxml.html import fromstring

channel_url = ""
processes = []


def get_channel():
    global channel_url
    channel_url = "https://twitch.tv/kevjrobbo"


def get_proxies():
    # url = 'https://free-proxy-list.net/'
    url = 'https://free-proxy-list.net/uk-proxy.html'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
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
        response = subprocess.Popen(
            ["livestreamer.exe", "--http-header", "Client-ID=",
            channel_url, "-j"], stdout=subprocess.PIPE).communicate()[0]
    except subprocess.CalledProcessError:
        print ("An error has occurred while trying to get the stream data. Is the channel online? Is the channel name correct?")
        sys.exit(1)
    except OSError:
        print ("An error has occurred while trying to use livestreamer package. Is it installed? Do you have Python in your PATH variable?")
 
    try:
        url = json.loads(response)['streams']['audio_only']['url']
    except:
        try:
            url = json.loads(response)['streams']['worst']['url']
        except (ValueError, KeyError):
            print ("An error has occurred while trying to get the stream data. Is the channel online? Is the channel name correct?")
            sys.exit(1)
 
    return url


def open_url(url, proxy):
    # Sending HEAD requests
    while True:
        try:
            with requests.Session() as s:
                response = s.head(url, proxies=proxy)
            print("Sent HEAD request with %s" % proxy["http"])
            print(response)
            time.sleep(20)
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
                        "http": proxy}}))

        print('Preparing .'),

    print('')

if __name__ == "__main__":
    print("Obtaining the channel...")
    get_channel()
    print("Obtained the channel")
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
