from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('source', models.CharField(
                    choices=[('newsapi', 'News API'), ('rss', 'RSS Feed'), ('mock', 'Mock Data')],
                    default='mock',
                    max_length=100
                )),
                ('body', models.TextField()),
                ('last_updated', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-last_updated'],
            },
        ),
    ]
