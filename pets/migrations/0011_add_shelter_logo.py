from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0010_alter_petcaretip_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelter',
            name='logo',
            field=models.ImageField(upload_to='shelters/', null=True, blank=True),
        ),
    ]
