import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import threading
import argparse

#grab arguments from command line
parser = argparse.ArgumentParser(description='Regularly check for a change in the first paragraph tag of a webpage')
parser.add_argument('webpage', metavar='url', type=str, help='url to check')
parser.add_argument('phoneTo', metavar='phone_out', type=str, help='phone to message updates to')
parser.add_argument('phoneFrom', metavar='phone_in', type=str, help='your Twilio phone number')
parser.add_argument('sid', metavar='account_sid', type=str, help='your Twilio SID')
parser.add_argument('auth', metavar='auth_token', type=str, help='your Twilio Auth Token')
parser.add_argument('--sec', metavar='secs', dest='seconds', type=float, default=10.0, help='modify how many seconds pass between checks (default 10s, float)')
parser.add_argument('--dur', metavar='duration', dest='checkTime', type=float, default=1.0, help='modify how many minutes to check the webpage for (default 1min, float)')

args = parser.parse_args()

#passing arguments from command line to variables
secs = args.seconds
mins = args.checkTime
phoneTo = args.phoneTo
phoneFrom = args.phoneFrom
account_sid = args.sid
auth_token = args.auth

client = Client(account_sid, auth_token)

#the following 2 if statements are limitations based on what I thought would be reasonable
if secs<3:
    secs = 3
    
if mins>10:
    mins = 10

#calculates how many times to run the scraper before stopping itself
counter = 1
n = (mins*60)/secs

#scraper
def scrape():
    #spaces out individual checks
    print("")
    
    #timer
    global account_sid
    global auth_token
    global client
    global counter
    global n
    global sec
    t = threading.Timer(secs, scrape)
    t.start()
    counter += 1
    if counter>n:
        t.cancel()
    
    #webscraper and comparison
    with open('save.txt', 'a+') as myfile:
        myfile.seek(0)
        oldtext=myfile.read()
        print("Old text: " + oldtext)
    page = requests.get("https://zoonn123.github.io/HolidayContest/")
    soup = BeautifulSoup(page.content, 'html.parser')
    if page.status_code==200:
        text = soup.find('p').get_text()
        if(str(oldtext) != str(text)):
            print("Text is different")
            message = client.messages.create(body='The first paragraph changed! The old text was: ' + oldtext + ', and the new text is: ' + text, from_=phoneFrom, to=phoneTo)
            with open('save.txt', 'w+') as myfile:
                myfile.write(str(text))
        else:
            print("Text is the same")
        print("New text: " + text)
    else:
        print("Error code: " + str(page.status_code) + " Page not accessible")

scrape()
