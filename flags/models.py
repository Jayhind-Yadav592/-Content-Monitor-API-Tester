from django.db import models
from keywords.models import Keyword
from content.models import ContentItem


class Flag(models.Model):
    """
    PDF Requirement: Flag model
    Stores relationship between keyword and matched content item.
    Fields: keyword, content_item, score, status
    Status choices: pending, relevant, irrelevant

    SUPPRESSION LOGIC (PDF's most important rule):
    - If status = irrelevant, flag stays suppressed
    - Unless ContentItem.last_updated changes after flag was reviewed
    - reviewed_at field tracks when reviewer made the decision
    """

    STATUS_PENDING = 'pending'
    STATUS_RELEVANT = 'relevant'
    STATUS_IRRELEVANT = 'irrelevant'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RELEVANT, 'Relevant'),
        (STATUS_IRRELEVANT, 'Irrelevant'),
    ]

    keyword = models.ForeignKey(
        Keyword,
        on_delete=models.CASCADE,
        related_name='flags'
    )
    content_item = models.ForeignKey(
        ContentItem,
        on_delete=models.CASCADE,
        related_name='flags'
    )
    score = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    # Used for suppression logic:
    # We compare content_item.last_updated with this timestamp
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Flag: '{self.keyword.name}' in '{self.content_item.title}' | Score: {self.score} | Status: {self.status}"

    class Meta:
        ordering = ['-score', '-created_at']
        unique_together = ['keyword', 'content_item']
