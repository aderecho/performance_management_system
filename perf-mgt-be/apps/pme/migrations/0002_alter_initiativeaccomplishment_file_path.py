from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pme", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="initiativeaccomplishment",
            name="file_path",
            field=models.FileField(
                upload_to="pme/evidence/",
                null=True,
                blank=True,
            ),
        ),
    ]
