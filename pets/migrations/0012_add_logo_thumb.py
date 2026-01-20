from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0011_add_shelter_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelter',
            name='logo_thumb',
            field=models.ImageField(upload_to='shelters/thumbs/', null=True, blank=True),
        ),
    ]
