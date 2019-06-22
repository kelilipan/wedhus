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
    return a.strip()


def remove_mention(text):
    temp = text.split()
    for i in range(len(temp)):
        if temp[i][0] != "@":
            break
        else:
            temp[i] = ""
    return (' '.join(temp).strip())


def get_last_id():
    return ref.get()


def get_status(id):
    return api.get_status(id, tweet_mode='extended')


def debug(data):
    ref = db.reference('/logs')
    ref.push(data)


def check(status):
    if('#quoteit' in status.text.lower()):
        return True
    else:
        return False


def bot():
    print("get mention")
    last_id = get_last_id()
    mentions = api.mentions_timeline(last_id['last_seen_id'])
    for mention in reversed(mentions):
        uname = '@' + str(mention.in_reply_to_screen_name)
        print('=============================================')
        print(mention.in_reply_to_status_id_str+" - " + uname)
        # debug(mention._json)
        if(mention.in_reply_to_status_id):
            mainStatus = get_status(mention.in_reply_to_status_id_str)
            if(check(mention)):
                print(mainStatus.full_text)
                status = remove_mention(
                    remove_media(mainStatus.full_text))
                img = json.loads(get_image())
                desc = ' by ' + img['user']['username'] + \
                    ' unsplash ' + img['links']['html']
                print(desc)
                try:
                    upload(img)
                    generate(status,  uname)
                    media_ids = api.media_upload('temp.jpg')
                    api.update_status(status='@'+mention.user.screen_name
                                      + desc, media_ids=[media_ids.media_id],
                                      in_reply_to_status_id=mention.id)
                except Exception as e:
                    print("------error: " + str(e))
                    store_last_id(mention.id)
            else:
                print("No hashtag")
            store_last_id(mention.id)
    print('=============================================')


while True:
    bot()
    time.sleep(60)
