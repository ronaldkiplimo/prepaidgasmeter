from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meters", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meter",
            name="meter_type",
            field=models.CharField(
                choices=[
                    ("residential", "Residential"),
                    ("commercial", "Commercial"),
                    ("prepaid", "Prepaid"),
                ],
                default="prepaid",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="meter",
            name="utility_provider",
            field=models.CharField(default="Gas Provider", max_length=100),
        ),
    ]
