from config import *
import tweepy
import firebase_admin
import json
import time
from firebase_admin import credentials, db

cred = credentials.Certificate("key.json")  # firebase_admin SDK
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://akusiap.firebaseio.com/'
})
ref = db.reference('/bot')
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)


def store_last_id(id):
    ref.set({
        'last_seen_id': id
    })


def get_last_id():
    return ref.get()


def get_status(id):
    return api.get_status(id)


def bot():
    last_id = get_last_id()
    mentions = api.mentions_timeline(last_id['last_seen_id'])
    for mention in reversed(mentions):
        print(mention.id_str+" - " + mention.text)
        if(mention.in_reply_to_status_id):
            mainStatus = get_status(mention.in_reply_to_status_id_str)
            print('aku disebut')
            store_last_id(mention.id)
            api.update_status('@' + mention.user.screen_name
                              + ' ' + mainStatus.text + " jancok", mention.id)


while True:
    bot()
    time.sleep(60)
