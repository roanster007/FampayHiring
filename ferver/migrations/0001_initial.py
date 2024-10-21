# Generated by Django 5.1.2 on 2024-10-21 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "video_id",
                    models.TextField(db_index=True, primary_key=True, serialize=False),
                ),
                ("title", models.TextField(max_length=100)),
                ("description", models.TextField(max_length=5000)),
                ("published_date", models.DateTimeField(db_index=True)),
                ("thumbnail_url", models.URLField()),
            ],
            options={
                "ordering": ["-published_date"],
            },
        ),
    ]
