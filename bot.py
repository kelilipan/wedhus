from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET
import tweepy
import firebase_admin
import json
import time
from image import generate, upload, get_image
import re
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


def remove_media(text):
    a = re.sub(r'https?:\/\/.*[\r\n]*', '', text)
    return a


def get_last_id():
    return ref.get()


def get_status(id):
    return api.get_status(id)


def debug(data):
    ref = db.reference('/logs')
    ref.push(data)


def check(screen_name):
    if (screen_name == 'Quoteitbot'):
        return False
    else:
        return True


def bot():
    last_id = get_last_id()
    mentions = api.mentions_timeline(last_id['last_seen_id'])
    for mention in reversed(mentions):
        uname = '@' + str(mention.in_reply_to_screen_name)
        print('=============================================')
        print(mention.id_str+" - " + uname)
        # debug(mention._json)
        if(mention.in_reply_to_status_id):
            mainStatus = get_status(mention.in_reply_to_status_id_str)
            if(check(mainStatus)):
                print(mainStatus.text)
                status = remove_media(mainStatus.text)
                img = json.loads(get_image())
                desc = ' by ' + img['user']['username'] + \
                    ' unsplash ' + img['links']['html']
                print(desc)
                try:
                    upload(img)
                except:
                    print('failed to upload image')
                try:
                    generate(status,  uname)
                except:
                    print("error generate image")
                try:
                    media_ids = api.media_upload('temp.jpg')
                except:
                    print("Failed to upload media")
                try:
                    api.update_status(status='@'+mention.user.screen_name
                                      + desc, media_ids=[media_ids.media_id],
                                      in_reply_to_status_id=mention.id)
                except tweepy.error.TweepError as error:
                    print('Unknown error', error)
            store_last_id(mention.id)


while True:
    bot()
    time.sleep(60)
