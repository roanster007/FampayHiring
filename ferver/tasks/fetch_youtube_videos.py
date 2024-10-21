from celery import shared_task
from datetime import datetime
from django.conf import settings
import requests
import os

from dotenv import load_dotenv

from ferver.models.videos import Video

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
GET_TYPE = "video"
ORDER_BY = "date"
MAX_RESULTS = 30


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

    latest_video = Video.objects.first()
    latest_video_id = latest_video.video_id if latest_video is not None else None

    videos = get_video_objects(video_items, latest_video_id)
    Video.objects.bulk_create(videos)


def get_video_objects(video_items, latest_video_id):
    videos = []

    for item in video_items:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]

        title = snippet["title"]
        description = snippet["description"]

        # We remove the additional 'Z' at end in publishTime, and convert
        # it to datetime object.
        published_date = datetime.fromisoformat(snippet["publishedAt"][:-1])
        thumbnail_url = snippet["thumbnails"]["default"]["url"]

        # We stop the moment we reach the first video that is present
        # in the database. Since all the entries of the database are
        # already sorted, the entries in the response after this entry
        # should already be present in the database.
        if latest_video_id is not None and video_id == latest_video_id:
            break

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
    # RFC 3339. (eg 1970-01-01T00:00:00Z)
    rfc3339_datetime = current_datetime.isoformat() + "Z"
    return rfc3339_datetime
