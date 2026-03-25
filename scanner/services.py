from django.utils import timezone
from keywords.models import Keyword
from content.models import ContentItem
from flags.models import Flag


def calculate_score(keyword_name: str, content_item: ContentItem) -> int:
    """
    Simple deterministic scoring

    - Exact match in title  → 100
    - Partial match in title → 70
    - Only in body          → 40
    - No match              → 0
    """
    kw = keyword_name.lower().strip()
    title = content_item.title.lower()
    body = content_item.body.lower()

    # Exact match: keyword == full title
    if kw == title:
        return 100

    # Partial match: keyword is part of title
    if kw in title:
        return 70

    # Body only match
    if kw in body:
        return 40

    return 0


def should_create_or_reset_flag(keyword: Keyword, content_item: ContentItem) -> bool:
    """
    If a flag was previously marked as 'irrelevant', it should NOT
    reappear on later scans UNLESS content_item.last_updated changed.

    Returns:
        True  → Create or reset the flag (surface it to reviewer)
        False → Suppress it (do not surface again)
    """
    try:
        existing_flag = Flag.objects.get(
            keyword=keyword,
            content_item=content_item
        )
    except Flag.DoesNotExist:
        return True

    # If flag is irrelevant, check if content changed
    if existing_flag.status == Flag.STATUS_IRRELEVANT:
        if existing_flag.reviewed_at is None:
            return True

        # KEY CHECK: Was content updated AFTER reviewer marked it irrelevant?
        if content_item.last_updated > existing_flag.reviewed_at:
            # Content changed → reset flag and resurface
            existing_flag.status = Flag.STATUS_PENDING
            existing_flag.reviewed_at = None
            existing_flag.score = calculate_score(keyword.name, content_item)
            existing_flag.save()
            return False  # Already updated, skip re-creation

        # Content NOT changed → stay suppressed
        return False

    # Flag exists but is pending or relevant → update score only
    return False


def run_scan() -> dict:
    keywords = Keyword.objects.all()
    content_items = ContentItem.objects.all()

    if not keywords.exists():
        return {
            "status": "skipped",
            "message": "No keywords found. Add keywords first via POST /keywords/",
            "flags_created": 0,
            "flags_suppressed": 0,
        }

    if not content_items.exists():
        return {
            "status": "skipped",
            "message": "No content items found. Load mock data first.",
            "flags_created": 0,
            "flags_suppressed": 0,
        }

    flags_created = 0
    flags_suppressed = 0

    for keyword in keywords:
        for content_item in content_items:

            score = calculate_score(keyword.name, content_item)

            # No match at all → skip
            if score == 0:
                continue

            # Check suppression rule
            create_flag = should_create_or_reset_flag(keyword, content_item)

            if create_flag:
                Flag.objects.update_or_create(
                    keyword=keyword,
                    content_item=content_item,
                    defaults={
                        'score': score,
                        'status': Flag.STATUS_PENDING,
                        'reviewed_at': None,
                    }
                )
                flags_created += 1
            else:
                # Check if it was suppressed (irrelevant and content unchanged)
                existing = Flag.objects.filter(
                    keyword=keyword,
                    content_item=content_item,
                    status=Flag.STATUS_IRRELEVANT
                ).first()
                if existing:
                    flags_suppressed += 1

    return {
        "status": "success",
        "message": "Scan completed",
        "keywords_scanned": keywords.count(),
        "content_items_scanned": content_items.count(),
        "flags_created_or_updated": flags_created,
        "flags_suppressed": flags_suppressed,
    }


def load_mock_data() -> dict:
    """
    Alternative Option: Use a local mock JSON dataset.
    Loads predefined mock articles into ContentItem table.
    """
    mock_articles = [
        {
            "title": "Learn Django Fast",
            "body": "Django is a powerful Python web framework used for building APIs and web applications quickly.",
            "source": "mock",
            "last_updated": "2026-03-20T10:00:00Z"
        },
        {
            "title": "Python for Data Science",
            "body": "Python is widely used in data science, machine learning, and automation workflows.",
            "source": "mock",
            "last_updated": "2026-03-20T11:00:00Z"
        },
        {
            "title": "Cooking Tips for Beginners",
            "body": "Best recipes and cooking techniques for people who are new to the kitchen.",
            "source": "mock",
            "last_updated": "2026-03-20T09:00:00Z"
        },
        {
            "title": "Automation in Modern Industry",
            "body": "Industrial automation is transforming manufacturing with robotics and AI integration.",
            "source": "mock",
            "last_updated": "2026-03-21T08:00:00Z"
        },
        {
            "title": "Building a Data Pipeline",
            "body": "A data pipeline automates the flow of data from source to destination for analytics.",
            "source": "mock",
            "last_updated": "2026-03-21T09:00:00Z"
        },
        {
            "title": "Travel Guide: Europe 2026",
            "body": "Top destinations in Europe for budget travelers this summer season.",
            "source": "mock",
            "last_updated": "2026-03-19T12:00:00Z"
        },
        {
            "title": "Django REST Framework Tutorial",
            "body": "Learn how to build RESTful APIs using Django REST Framework step by step.",
            "source": "mock",
            "last_updated": "2026-03-22T07:00:00Z"
        },
        {
            "title": "Introduction to Python",
            "body": "Python is a beginner-friendly programming language with a simple and readable syntax.",
            "source": "mock",
            "last_updated": "2026-03-22T08:00:00Z"
        },
    ]

    created_count = 0
    skipped_count = 0

    from django.utils.dateparse import parse_datetime

    for article in mock_articles:
        obj, created = ContentItem.objects.update_or_create(
            title=article['title'],
            defaults={
                'body': article['body'],
                'source': article['source'],
                'last_updated': parse_datetime(article['last_updated']),
            }
        )
        if created:
            created_count += 1
        else:
            skipped_count += 1

    return {
        "status": "success",
        "message": "Mock data loaded into ContentItem table",
        "created": created_count,
        "already_existed": skipped_count,
        "total": len(mock_articles)
    }
