import urllib.request
import cloudinary.uploader
import json
from config import UNSPLASH_KEY, cloud_name, api_key, api_secret
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)
opener = urllib.request.build_opener()
opener.addheaders = [('Authorization',  'Client-ID '+UNSPLASH_KEY)]
urllib.request.install_opener(opener)


def get_image():
    req = urllib.request.Request(
        'http://api.unsplash.com/photos/random')
    image = urllib.request.urlopen(req).read()
    return image


def clear_temp():
    cloudinary.api.delete_resources(["temp"])


def upload(image):
    clear_temp()
    image_link = image['links']['download_location']
    js = json.loads(urllib.request.urlopen(image_link).read())
    link = js['url']
    print(link)
    cloudinary.uploader.upload(
        link,
        public_id='temp',
        headers='Authorization: Client-ID '+UNSPLASH_KEY)


def generate(quote,  user):
    option = [
        {'width': 1024, 'height': 1024, 'crop': "fill"},
        {
            "effect": {'blur': 300}
        },
        {'width': 800,
         'overlay': {
             'font_family': "Times",
             'font_size': 58,
             'font_weight': "bold",
             'text_align': "center",
             'text': quote},
         'color': 'white',
         'crop': "fit"},
        {'overlay':
         {'font_family': "yellowtail",
          'font_size': 35,
          #   'font_weight': "bold",
          'text': user},
         'color': 'white',
         'gravity': "south",
         'y': 100}
    ]
    curl = cloudinary.utils.cloudinary_url
    edit = curl('temp',
                transformation=option)
    urllib.request.urlretrieve(edit[0], 'temp.jpg')
    return(edit[0])


# clear_temp()
# upload()
# generate("asnjdnaksjdnasndjkasnjkdnjkasndjknas", '@raisoturu')
# img = json.loads(get_image())
