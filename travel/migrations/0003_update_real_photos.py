from django.db import migrations


DESTINATION_PHOTOS = {
    'pulau-derawan': {
        'hero_image': 'travel/img/noah-maratua-resort.jpeg',
        'image': 'travel/img/sienna-resort-maratua.jpeg',
    },
    'bukit-bangkirai': {
        'hero_image': 'travel/img/samboja-lodge.jpeg',
        'image': 'travel/img/bangkirai-eco-lodge.jpeg',
    },
    'pulau-kumala': {
        'hero_image': 'travel/img/rumah-odah-rehat.jpeg',
        'image': 'travel/img/hotel-grand-fatma-tenggarong.jpeg',
    },
    'labuan-cermin': {
        'hero_image': 'travel/img/lamin-guntur-eco-lodge.jpeg',
        'image': 'travel/img/thrive-inn.jpeg',
    },
}

ROOM_PHOTOS = {
    'noah-maratua-resort': 'travel/img/noah-maratua-resort.jpeg',
    'sienna-resort-maratua': 'travel/img/sienna-resort-maratua.jpeg',
    'samboja-lodge': 'travel/img/samboja-lodge.jpeg',
    'bangkirai-eco-lodge': 'travel/img/bangkirai-eco-lodge.jpeg',
    'hotel-grand-fatma-tenggarong': 'travel/img/hotel-grand-fatma-tenggarong.jpeg',
    'rumah-odah-rehat': 'travel/img/rumah-odah-rehat.jpeg',
    'lamin-guntur-eco-lodge': 'travel/img/lamin-guntur-eco-lodge.jpeg',
    'thrive-inn': 'travel/img/thrive-inn.jpeg',
}


def update_real_photos(apps, schema_editor):
    Destination = apps.get_model('travel', 'Destination')
    Room = apps.get_model('travel', 'Room')

    for slug, data in DESTINATION_PHOTOS.items():
        Destination.objects.filter(slug=slug).update(**data)

    for slug, image in ROOM_PHOTOS.items():
        Room.objects.filter(slug=slug).update(image=image)


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0002_seed_initial_data'),
    ]

    operations = [
        migrations.RunPython(update_real_photos, migrations.RunPython.noop),
    ]
