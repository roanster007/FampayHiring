# FamPay-Hiring-Assignment

Backend Assignment (Intern)

## Project Goal

To make an API to fetch latest videos sorted in reverse chronological order of their publishing date-time from YouTube for a given tag/search query in a paginated response.

## Features:

- Server calls the YouTube API continuously in background via `Celery Beat` at interval of `YOUTUBE_VIDEO_FETCH_TIME_PERIOD` for fetching the latest videos for a predefined search query -- `YOUTUBE_SEARCH_QUERY` and stores the data of videos (specifically these fields - Video title, description, publishing datetime, thumbnails URLs and any other fields you require) in a database with proper indexes.
- A GET API which returns the stored video data in a paginated response with max entries per page of `VIDEO_ENTRIES_PER_PAGE` sorted in descending order of published datetime.
- Can handle multiple API Keys passed as per the format described in `env_format.py`, so that if the quota on one of the APIs exceeds, the next available one is used, and the expired API is automatically removed.
- Scalable and Optimised.

## API Endpoints:

- `/videos` - Returns the first page of video fields (title, description, video_id, published_date, and thumbnail_url) in the reverse chronological order.
- `/videos/?page=2` - Returns the second page of video fields in reverse chronological order, counted from the last fetched video (offset pagination).
- `/videos/?page=2&last_publish_time=2024-10-20T19:12:07+00:00Z` - Returns the second page of video fields in reverse chronological order, counted from the last entry of the previous page (cursor pagination). Note that the `publish_time` is accepted in `RFC 3339` format.
  <br>
  All API responses are of the form:

```py
page: 2,
videos: [{video_id:,..}],
num_videos: 3
```

## TechStack Used

1. Python (Programming Language)<br>
2. Django (Web Framework)<br>
3. PostgreSQL (Database)<br>
4. Celery<br>
5. Redis<br>

## How to setup and run locally

<p>
  1. Clone the Repository <br>
  2. Create and  activate Python Virtual Environment </a></h5><br>
  3. After activating the virtual enviornment, redirect to project base directory. <br>
  4. Run the following command for installing dependencies.
</p>

    $ pip install -r requirements.txt

<br>
  5. Now before running the server, we have to setup database, so run.
 
    $ ./manage.py migrate

<br>
  6. Now run the following command for starting the dev environment (celery, redis, django server)

    $ ./tools/run-dev.py

<br>
Now run the APIs described in the Postman for testing the project at `http://localhost:8000`.

<br>
