import json
import requests
import os
import redis

from celery import shared_task
from datetime import datetime
from django.conf import settings

from dotenv import load_dotenv

from ferver.models.videos import Video

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
GET_TYPE = "video"
ORDER_BY = "date"
MAX_RESULTS = 10

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


@shared_task
def fetch_youtube_videos():
    request_url = generate_request_url()

    try:
        response = requests.get(request_url)
        response.raise_for_status()

    except requests.exceptions.HTTPError:
        print("Invalid API KEY!")
        return

    data = response.json()
    video_items = data["items"]

    videos = get_video_objects(video_items)
    Video.objects.bulk_create(videos)
    cache_current_session_video_ids(video_items)


def get_video_objects(video_items):
    videos = []
    previous_session_cache = redis_client.get('previous_session')

    if previous_session_cache is not None:
        previous_session_video_ids = json.loads(redis_client.get('previous_session'))

    for item in video_items:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]

        title = snippet["title"]
        description = snippet["description"]

        # We remove the additional 'Z' at end in publishTime, and convert
        # it to datetime object.
        published_date = datetime.fromisoformat(snippet["publishedAt"][:-1])
        thumbnail_url = snippet["thumbnails"]["default"]["url"]

        # If we encounter a video which is already present in previous
        # fetch, we ignore it.
        if previous_session_cache is not None and video_id in previous_session_video_ids:
            continue

        video_object = Video(
            video_id=video_id,
            title=title,
            description=description,
            published_date=published_date,
            thumbnail_url=thumbnail_url,
        )

        videos.append(video_object)

    return videos


def generate_request_url():
    current_datetime = get_current_datetime()

    request_url = (
        f"{settings.YOUTUBE_SEARCH_HTTP_ENDPOINT}?"
        f"key={API_KEY}&"
        f"q={settings.YOUTUBE_SEARCH_QUERY}&"
        f"type={GET_TYPE}&"
        f"part=snippet&"
        f"order={ORDER_BY}&"
        f"publishedAfter={current_datetime}&"
        f"maxResults={MAX_RESULTS}"
    )
    return request_url


def get_current_datetime():
    current_datetime = datetime.utcnow()

    # The datetime format supported by youtube api is
    # RFC 3339. (eg: "1970-01-01T00:00:00Z")
    rfc3339_datetime = current_datetime.isoformat() + "Z"
    return rfc3339_datetime


def cache_current_session_video_ids(video_items):
    video_ids = [item["id"]["videoId"] for item in video_items]
    redis_client.set('previous_session', json.dumps(video_ids))
