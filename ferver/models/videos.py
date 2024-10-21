from django.db import models

from datetime import datetime


class Video(models.Model):
    video_id = models.TextField(primary_key=True, db_index=True)

    # Max size for youtube video title is 5000
    title = models.TextField(max_length=100)
    # Max size for youtube video description is 5000
    description = models.TextField(max_length=5000)

    published_date = models.DateTimeField(auto_now=False, db_index=True)
    thumbnail_url = models.URLField()

    class Meta:
        ordering = ["-published_date"]
    
    def to_dict(self):
        published_date = self.published_date.isoformat() + "Z"

        return {
            "video_id": self.video_id,
            "title": self.title,
            "description": self.description,
            "published_date": published_date,
            "thumbnail_url": self.thumbnail_url,
        }
