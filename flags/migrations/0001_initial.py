from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('keywords', '0001_initial'),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('relevant', 'Relevant'),
                        ('irrelevant', 'Irrelevant'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('keyword', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='flags',
                    to='keywords.keyword'
                )),
                ('content_item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='flags',
                    to='content.contentitem'
                )),
            ],
            options={
                'ordering': ['-score', '-created_at'],
                'unique_together': {('keyword', 'content_item')},
            },
        ),
    ]
