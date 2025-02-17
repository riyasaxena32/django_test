# Generated by Django 5.0.2 on 2025-01-31 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faqs', '0002_faq_auto_translate_faq_last_translated'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimpleQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(verbose_name='Question')),
                ('answer', models.TextField(verbose_name='Answer')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Simple Question',
                'verbose_name_plural': 'Simple Questions',
                'ordering': ['-created_at'],
            },
        ),
    ]
