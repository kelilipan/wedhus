from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
import tweepy
import firebase_admin
import json
import time
from image import *
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
        uname = mention.user.screen_name
        print(mention.id_str+" - " + '@' + uname)
        if(mention.in_reply_to_status_id and '@quoteitbot' in mention.text.lower()):
            mainStatus = get_status(mention.in_reply_to_status_id_str)
            print(mainStatus.text)

            status = mainStatus.text
            img = get_image()
            upload(img)
            generate(status, '@' + uname)
            media_ids = api.media_upload('temp.jpg')
            print(media_ids.media_id)
            try:
                api.update_status(status='@' + uname
                                  + ' nyoh', media_ids=[media_ids.media_id],
                                  in_reply_to_status_id=mention.id)
            except tweepy.error.TweepError as error:
                print('Unknown error', error)
            store_last_id(mention.id)


while True:
    bot()
    time.sleep(60)
