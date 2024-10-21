from django.conf import settings

from datetime import datetime

from ferver.models.videos import Video

VIDEO_ENTRIES_PER_PAGE = settings.VIDEO_ENTRIES_PER_PAGE


def maybe_get_paginated_video_data(page, last_publish_time):
    if last_publish_time is not None:
        # In presence of the last published time, we try to return
        # a page with entries older than the last published time,
        # with at most entries of max size of page.
        last_publish_time_object = datetime.fromisoformat(
            last_publish_time.replace("00:00Z", "")
        )

        videos_in_page = Video.objects.filter(
            published_date__lt=last_publish_time_object
        ).order_by("-published_date")[: VIDEO_ENTRIES_PER_PAGE + 1]

    else:
        # In absence of the last published time, return page
        # of size of max entries of page querying from the
        # first entry.
        entries_to_skip = VIDEO_ENTRIES_PER_PAGE * (page - 1)
        videos_in_page = Video.objects.all().order_by("-published_date")[
            entries_to_skip + 1 : entries_to_skip + VIDEO_ENTRIES_PER_PAGE + 1
        ]

    paginated_video_data = [video.to_dict() for video in videos_in_page]

    return paginated_video_data
