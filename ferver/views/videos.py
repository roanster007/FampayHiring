from django.http import JsonResponse
from django.views import View

from datetime import datetime

from ferver.actions.videos import maybe_get_paginated_video_data


class Video(View):
    def get(self, request):
        # Default page to 1 if no page is provided.
        page = request.GET.get("page", 1)

        # last_publish_time is important because it determines the
        # cursor position for the pagination. last_publish_time
        # is of RFC 3339 format. (eg: "1970-01-01T00:00:00Z")
        last_publish_time = request.GET.get("last_publish_time")

        try:
            page = int(page)
        except ValueError:
            return JsonResponse(
                {"error": "Page parameter must be an integer."}, status=400
            )

        paginated_video_data = maybe_get_paginated_video_data(page, last_publish_time)

        response_data = {
            "page": page,
            "videos": paginated_video_data,
            "num_videos": len(paginated_video_data),
        }

        return JsonResponse(response_data)
