# twitch-viewer
A viewer bot for twitch.tv based off https://github.com/ohyou/twitch-viewer 

This has been updated to bring in a MAX list of free proxy URLS from https://free-proxy-list.net/uk-proxy.html dynamically and also all can be ran via a single command.

## How to Install
The application was developed with Python 2.7.10 using the following libraries (installed using pip):
- pip install requests
- pip install json
- pip install streamlink
- pip install lxml

Note that json may be included into your python distributive.
To test a packages for availability, type thise commands into console:
- python
- import json
- import requests
- import livestreamer
If everything's fine, proceed.

## How to Run
I have setup this script to be ran dynamically via commandline. In order to run it, al you have to do is the following:

`python twitch-viewer.py CLIENT-ID TWITCH-USER NO-OF-PROXIES RUNTIME`

- CLIENT-ID: THis is aquired via the Twitch Developer API Dashboard by making a New app (https://glass.twitch.tv/console/apps)
- TWITCH-USER:  THis is the Twich user you want to run the views against
- NO-OF-PROXIES: Specify the number of proxies you want to run.  Its currently getting it dynamically via https://free-proxy-list.net/uk-proxy.html and it has a limit of 20
- RUNTIME: THis is how long you want to scipt to run e.g. 1 hour = 3600, 2 hours 7200, 3 hours = 10800

The "viewers" you get only work through proxy.  The amount of viewers you get equals to the amount of proxies specified.

The application starts working within ~10 seconds, and you will get viewers within a couple minutes (it takes some time for twitch to process the connections).

<a href="https://www.buymeacoffee.com/disruptthinking" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>