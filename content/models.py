from django.db import models


class ContentItem(models.Model):
    SOURCE_CHOICES = [
        ('newsapi', 'News API'),
        ('rss', 'RSS Feed'),
        ('mock', 'Mock Data'),
    ]

    title = models.CharField(max_length=500)
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES, default='mock')
    body = models.TextField()
    last_updated = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-last_updated']
