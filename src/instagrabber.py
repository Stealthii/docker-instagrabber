#!/usr/bin/env python

import errno
import json
import logging
import os
import requests

from apscheduler.schedulers.blocking import BlockingScheduler
from instagram.bind import InstagramAPIError
from instagram.bind import InstagramClientError
from instagram.client import InstagramAPI

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
tag_name = os.environ['TAG_NAME']
refresh_interval = os.environ['REFRESH_INTERVAL'] or 5

output_dir = os.environ['OUTPUT_DIR']
output_path = "/srv" + output_dir

big_json = output_path + ".json"

try:
    os.makedirs(output_path)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise

try:
    api = InstagramAPI(client_id=client_id, client_secret=client_secret)
except InstagramClientError as e:
    logging.error("Instagrabber: Client error - {}".format(e.error_message))
    raise


def get_images():
    try:
        media_list, _ = api.tag_recent_media(tag_name=tag_name, count=20)
    except InstagramAPIError as e:
        logging.warning("Instagrabber: API error - {}".format(e.error_message))

    for media in media_list:
        if media.type != 'image':
            pass  # fuck videos man

        # Name file after media id
        file_name = media.id + ".jpg"
        json_name = media.id + ".json"
        file_path = os.path.join(output_path, file_name)
        json_path = os.path.join(output_path, json_name)
        if not (os.path.exists(file_path) and os.path.exists(json_path)):
            logging.info("Instagrabber: Downloading {}...".format(media.id))
            r = requests.get(media.images['standard_resolution'].url)
            with open(file_path, 'wb') as f:
                f.write(r.content)

            # JSON data
            file_info = json.dumps(
                {
                    # "caption": media.caption,
                    "filename": file_name,
                    "path": file_path,
                    "url": os.path.join(output_dir, file_name),
                    "tags": [tag.name for tag in media.tags]
                }
            )
            with open(json_path, 'wb') as j:
                j.write(file_info)


def refresh_json():
    with open(big_json, 'wb') as j:
        big_data = []
        for json_file in os.listdir(output_path):
            if json_file.endswith(".json"):
                file_path = os.path.join(output_path, json_file)
                try:
                    json_data = open(file_path).read()
                    data = json.loads(json_data)
                    big_data.append(data)
                except:
                    pass  # No failures for now

        j.write(json.dumps(big_data))


def be_righteous():
    get_images()
    refresh_json()


if __name__ == "__main__":
    be_righteous()  # do one now for good measure
    scheduler = BlockingScheduler()
    scheduler.add_job(be_righteous, 'interval', minutes=refresh_interval)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
