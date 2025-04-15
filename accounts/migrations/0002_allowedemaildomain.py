# Generated manually for AllowedEmailDomain model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedEmailDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(help_text="Domain name without @ (e.g., 'company.com')", max_length=100, unique=True)),
                ('description', models.CharField(blank=True, help_text='Optional description or organization name', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='If unchecked, this domain will not be allowed for registration')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Allowed Email Domain',
                'verbose_name_plural': 'Allowed Email Domains',
                'ordering': ['domain'],
            },
        ),
    ]