from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0025_projectrequest_projectbid'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventrequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Approval'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
