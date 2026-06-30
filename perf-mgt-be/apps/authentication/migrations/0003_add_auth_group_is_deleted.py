from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_rename_date_joined_user_created_at_user_updated_at"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE auth_group "
                "ADD COLUMN IF NOT EXISTS is_deleted boolean NOT NULL DEFAULT false"
            ),
            reverse_sql=(
                "ALTER TABLE auth_group "
                "DROP COLUMN IF EXISTS is_deleted"
            ),
        ),
    ]
