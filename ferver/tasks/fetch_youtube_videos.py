import dotenv
import json
import requests
import os
import redis

from celery import shared_task
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse


from ferver.models.videos import Video

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv()

API_KEYS = os.environ.get("YOUTUBE_API_KEYS").split(", ")
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
    if not API_KEYS:
        raise JsonResponse({"error": "No Valid API Keys Provided!"}, status=401)

    API_KEY = API_KEYS[0]

    request_url = generate_request_url(API_KEY)

    try:
        response = requests.get(request_url)
        response.raise_for_status()

    except requests.exceptions.HTTPError:
        # If the current API Key is expired, or has its quota
        # exceeded, we try to use the next available API Key
        # after a delay of 5 second.
        if 400 <= response.status_code < 500:
            API_KEYS.pop(0)
            os.environ["YOUTUBE_API_KEYS"] = json.dumps(API_KEYS)
            dotenv.set_key(dotenv_file, "YOUTUBE_API_KEYS", json.dumps(API_KEYS))
            fetch_youtube_videos.apply_async(countdown=5)
            return

        else:
            response.raise_for_status

    data = response.json()
    video_items = data["items"]

    videos = get_video_objects(video_items)
    Video.objects.bulk_create(videos)
    cache_current_session_video_ids(video_items)


def get_video_objects(video_items):
    videos = []
    previous_session_cache = redis_client.get("previous_session")

    if previous_session_cache is not None:
        previous_session_video_ids = json.loads(redis_client.get("previous_session"))

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
        if (
            previous_session_cache is not None
            and video_id in previous_session_video_ids
        ):
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


def generate_request_url(API_KEY):
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
    redis_client.set("previous_session", json.dumps(video_ids))
