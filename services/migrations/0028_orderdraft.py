from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0027_ordertask'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Optional label for this draft', max_length=255)),
                ('file', models.FileField(upload_to='order_drafts/%Y/%m/')),
                ('note', models.TextField(blank=True, help_text='Optional note from freelancer to client')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='drafts',
                    to='services.order',
                )),
                ('uploaded_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='auth.user',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
