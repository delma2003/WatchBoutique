from django.db import migrations

def set_wrist_sizes(apps, schema_editor):
    Watch = apps.get_model('app', 'Watch')
    # Update watches based on their case_size
    Watch.objects.filter(case_size='small').update(wrist_size='xs')
    Watch.objects.filter(case_size='medium').update(wrist_size='m')
    Watch.objects.filter(case_size='large').update(wrist_size='xl')
    # Set some default diameters
    Watch.objects.filter(case_size='small').update(case_diameter=34)
    Watch.objects.filter(case_size='medium').update(case_diameter=40)
    Watch.objects.filter(case_size='large').update(case_diameter=46)

def reverse_func(apps, schema_editor):
    Watch = apps.get_model('app', 'Watch')
    # Revert the changes if needed
    Watch.objects.all().update(wrist_size=None, case_diameter=None)

class Migration(migrations.Migration):
    dependencies = [
        # Replace with your last migration file number
        ('app', '0020_watch_adjustable_watch_band_length_watch_band_width_and_more'),
    ]

    operations = [
        migrations.RunPython(set_wrist_sizes, reverse_func),
    ]