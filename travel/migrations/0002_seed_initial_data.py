from django.db import migrations


DESTINATIONS = [
    {
        'slug': 'pulau-derawan',
        'name': 'Pulau Derawan',
        'location': 'Berau, Kalimantan Timur',
        'subtitle': 'Resort dan penginapan dekat laut biru Derawan.',
        'hero_image': 'travel/img/noah-maratua-resort.jpeg',
        'image': 'travel/img/noah-maratua-resort.jpeg',
    },
    {
        'slug': 'bukit-bangkirai',
        'name': 'Bukit Bangkirai',
        'location': 'Kutai Kartanegara, Kalimantan Timur',
        'subtitle': 'Penginapan dan lodge dekat kawasan hutan Bangkirai.',
        'hero_image': 'travel/img/samboja-lodge.jpeg',
        'image': 'travel/img/samboja-lodge.jpeg',
    },
    {
        'slug': 'pulau-kumala',
        'name': 'Pulau Kumala',
        'location': 'Tenggarong, Kalimantan Timur',
        'subtitle': 'Akomodasi dekat Tenggarong dan area Pulau Kumala.',
        'hero_image': 'travel/img/rumah-odah-rehat.jpeg',
        'image': 'travel/img/rumah-odah-rehat.jpeg',
    },
    {
        'slug': 'labuan-cermin',
        'name': 'Labuan Cermin',
        'location': 'Biduk-biduk, Berau',
        'subtitle': 'Pilihan stay dekat danau jernih Labuan Cermin.',
        'hero_image': 'travel/img/lamin-guntur-eco-lodge.jpeg',
        'image': 'travel/img/lamin-guntur-eco-lodge.jpeg',
    },
]

ROOMS = [
    {
        'slug': 'noah-maratua-resort',
        'name': 'Noah Maratua Resort',
        'destination': 'pulau-derawan',
        'location': 'Maratua Island, Berau',
        'price_number': 1200000,
        'image': 'travel/img/noah-maratua-resort.jpeg',
        'stars': 5,
        'badge': 'Ocean View',
        'description': 'Resort tepi laut dengan pemandangan air biru, cocok untuk liburan keluarga dan pasangan.',
        'features': ['Ocean view', 'Breakfast', 'Private dock', 'Free wifi'],
        'category': 'Resort Hotel',
        'hotel_type': 'Villa',
        'capacity': 6,
        'latitude': 2.2358,
        'longitude': 118.6118,
    },
    {
        'slug': 'sienna-resort-maratua',
        'name': 'Sienna Resort Maratua',
        'destination': 'pulau-derawan',
        'location': 'Pulau Maratua, Berau',
        'price_number': 2300000,
        'image': 'travel/img/sienna-resort-maratua.jpeg',
        'stars': 5,
        'badge': 'Private Beach',
        'description': 'Penginapan premium dekat pantai dengan nuansa tropis dan area santai yang luas.',
        'features': ['Beach front', 'Pool access', 'Breakfast', 'Family room'],
        'category': 'Resort Hotel',
        'hotel_type': 'Villa',
        'capacity': 5,
        'latitude': 2.2164,
        'longitude': 118.5876,
    },
    {
        'slug': 'samboja-lodge',
        'name': 'Samboja Lodge',
        'destination': 'bukit-bangkirai',
        'location': 'Samboja, Kutai Kartanegara',
        'price_number': 1500000,
        'image': 'travel/img/samboja-lodge.jpeg',
        'stars': 5,
        'badge': 'Forest Stay',
        'description': 'Lodge bernuansa hutan, cocok untuk tamu yang ingin suasana tenang dan alami.',
        'features': ['Forest view', 'Nature walk', 'Restaurant', 'Guide area'],
        'category': 'Resort Hotel',
        'hotel_type': 'Hostel',
        'capacity': 4,
        'latitude': -1.0438,
        'longitude': 116.9877,
    },
    {
        'slug': 'bangkirai-eco-lodge',
        'name': 'Bangkirai Eco Lodge',
        'destination': 'bukit-bangkirai',
        'location': 'Bukit Bangkirai Area',
        'price_number': 600000,
        'image': 'travel/img/bangkirai-eco-lodge.jpeg',
        'stars': 4,
        'badge': 'Eco Lodge',
        'description': 'Eco lodge sederhana dekat kawasan wisata, nyaman untuk short stay dan eksplorasi alam.',
        'features': ['Eco stay', 'Parking area', 'Breakfast', 'Nature access'],
        'category': 'Resort Hotel',
        'hotel_type': 'Hostel',
        'capacity': 3,
        'latitude': -1.0063,
        'longitude': 116.8636,
    },
    {
        'slug': 'hotel-grand-fatma-tenggarong',
        'name': 'Hotel Grand Fatma Tenggarong',
        'destination': 'pulau-kumala',
        'location': 'Jl. Pesut, Tenggarong',
        'price_number': 530000,
        'image': 'travel/img/hotel-grand-fatma-tenggarong.jpeg',
        'stars': 3,
        'badge': 'City Hotel',
        'description': 'Hotel kota yang strategis untuk mengunjungi area Tenggarong dan Pulau Kumala.',
        'features': ['City center', 'Meeting room', 'Restaurant', 'Parking'],
        'category': 'City Hotel',
        'hotel_type': 'All',
        'capacity': 4,
        'latitude': -0.4149,
        'longitude': 116.9891,
    },
    {
        'slug': 'rumah-odah-rehat',
        'name': 'Rumah Odah Rehat',
        'destination': 'pulau-kumala',
        'location': 'Kutai Kartanegara',
        'price_number': 400000,
        'image': 'travel/img/rumah-odah-rehat.jpeg',
        'stars': 5,
        'badge': 'Homestay',
        'description': 'Homestay unik dengan bentuk bangunan menarik dan suasana lokal yang hangat.',
        'features': ['Homestay', 'Local vibes', 'Terrace', 'Family friendly'],
        'category': 'Residental Hotel',
        'hotel_type': 'Villa',
        'capacity': 6,
        'latitude': -0.4088,
        'longitude': 116.9869,
    },
    {
        'slug': 'lamin-guntur-eco-lodge',
        'name': 'Lamin Guntur Eco Lodge',
        'destination': 'labuan-cermin',
        'location': 'Biduk-biduk, Berau',
        'price_number': 600000,
        'image': 'travel/img/lamin-guntur-eco-lodge.jpeg',
        'stars': 4,
        'badge': 'Lake View',
        'description': 'Penginapan dekat kawasan danau jernih dengan pemandangan hijau dan udara segar.',
        'features': ['Lake access', 'Green view', 'Breakfast', 'Tour help'],
        'category': 'Resort Hotel',
        'hotel_type': 'Villa',
        'capacity': 5,
        'latitude': 1.2572,
        'longitude': 118.7975,
    },
    {
        'slug': 'thrive-inn',
        'name': 'Thrive Inn',
        'destination': 'labuan-cermin',
        'location': 'Biduk-biduk, Berau',
        'price_number': 350000,
        'image': 'travel/img/thrive-inn.jpeg',
        'stars': 5,
        'badge': 'Sunset View',
        'description': 'Inn dengan suasana santai dan pemandangan sore yang cocok untuk liburan singkat.',
        'features': ['Sunset view', 'Simple room', 'Wifi', 'Easy access'],
        'category': 'Motel',
        'hotel_type': 'All',
        'capacity': 2,
        'latitude': 1.2487,
        'longitude': 118.8052,
    },
]

REVIEWS = [
    {'name': 'Kang Jhon', 'time': '3 Hari Yang Lalu', 'text': 'The room was nice and tidy. Membuat istirahat jadi nyaman setelah jalan-jalan.', 'rating': 5, 'avatar': 'KJ'},
    {'name': 'Kang Ecep', 'time': '4 Hari Ago', 'text': 'View hotelnya bagus, tempatnya tenang, dan akses ke lokasi wisata cukup mudah.', 'rating': 5, 'avatar': 'KE'},
    {'name': 'Kardun', 'time': '2 Months Ago', 'text': 'Very satisfactory. Kamar bersih, pelayanan ramah, dan harganya sesuai.', 'rating': 4, 'avatar': 'KA'},
    {'name': 'Dodi', 'time': '1 Week Ago', 'text': 'Tempatnya cocok buat healing. Makanan lumayan dan area luarnya enak buat foto.', 'rating': 4, 'avatar': 'DO'},
    {'name': 'Supratman', 'time': '3 Years 2 Month Ago', 'text': 'Friendly service and comfortable rooms, very good untuk trip keluarga.', 'rating': 5, 'avatar': 'SU'},
]

HELP_ARTICLES = [
    {
        'slug': 'cancel-reservation',
        'title': 'How do I cancel my reservation?',
        'category': 'Paying for a reservation',
        'intro': 'Kamu bisa membatalkan reservasi melalui menu Account, bagian Payment atau riwayat booking yang sudah masuk.',
        'steps': ['Buka menu Account lalu pilih Payment atau data booking yang ingin dibatalkan.', 'Tekan tombol Cancel Booking pada pesanan yang masih aktif.', 'Baca syarat pembatalan, lalu konfirmasi pembatalan jika semua data sudah sesuai.', 'Sistem akan mengirimkan konfirmasi pembatalan setelah proses berhasil.'],
        'note': 'Jika pesanan sudah melewati batas waktu pembatalan, silakan hubungi Help Center untuk bantuan lanjutan.',
    },
    {
        'slug': 'cancellation-terms',
        'title': 'Room Booking Cancellation Terms and Conditions',
        'category': 'Paying for a reservation',
        'intro': 'Syarat pembatalan mengikuti kebijakan hotel dan waktu check-in yang kamu pilih.',
        'steps': ['Pembatalan gratis tersedia jika hotel masih mengizinkan refund.', 'Pembatalan mendekati tanggal check-in bisa dikenakan biaya.', 'Harga promo tertentu tidak dapat dibatalkan otomatis.'],
        'note': 'Selalu cek detail pesanan sebelum menekan tombol pembayaran.',
    },
    {
        'slug': 'cancel-unpaid',
        'title': 'How to cancel unpaid room Booking Pesanan',
        'category': 'Paying for a reservation',
        'intro': 'Pesanan yang belum dibayar bisa dibatalkan langsung dari halaman booking.',
        'steps': ['Masuk ke Account.', 'Buka Payment atau daftar pesanan.', 'Pilih pesanan yang belum dibayar lalu tekan Cancel.'],
        'note': 'Pesanan yang belum dibayar biasanya juga akan otomatis batal sesuai batas waktu sistem.',
    },
    {
        'slug': 'auto-cancel',
        'title': 'Room bookings are canceled automatically',
        'category': 'Paying for a reservation',
        'intro': 'Sistem dapat membatalkan booking otomatis ketika pembayaran tidak dilakukan sampai batas waktu.',
        'steps': ['Cek batas waktu pembayaran di halaman booking berhasil.', 'Lakukan pembayaran sebelum waktu habis.', 'Jika sudah batal, lakukan booking ulang dari halaman room.'],
        'note': 'Booking yang sudah otomatis batal tidak mengurangi saldo kamu.',
    },
    {
        'slug': 'change-password',
        'title': 'How to change password?',
        'category': 'Account & Security',
        'intro': 'Password bisa diubah dari halaman Account atau Forgot Password.',
        'steps': ['Buka Account.', 'Pilih Change password.', 'Masukkan nomor verifikasi dan password baru.'],
        'note': 'Gunakan password yang mudah kamu ingat tetapi sulit ditebak orang lain.',
    },
    {
        'slug': 'forgot-verification',
        'title': 'Forgot password verification number',
        'category': 'Account & Security',
        'intro': 'Nomor verifikasi dikirim ke email atau nomor ponsel yang terhubung dengan akun.',
        'steps': ['Buka Forgot Password.', 'Masukkan email atau nomor telepon.', 'Tekan Send lalu cek kode verifikasi.'],
        'note': 'Di project ini, tombol Send menampilkan status terkirim saja.',
    },
    {
        'slug': 'update-profile',
        'title': 'Update profile data and email address',
        'category': 'Account & Security',
        'intro': 'Data profile bisa diedit dari halaman Edit Profile.',
        'steps': ['Buka Account.', 'Klik Edit Profile.', 'Ubah username, email, nomor telepon, tanggal lahir, dan alamat.', 'Tekan Save Profile.'],
        'note': 'Data sudah disimpan ke database melalui model UserProfile.',
    },
    {
        'slug': 'room-facilities',
        'title': 'How to see room facilities?',
        'category': 'Hotel & Room',
        'intro': 'Fasilitas kamar tersedia di halaman detail room.',
        'steps': ['Buka Search Accommodation.', 'Pilih salah satu hotel.', 'Lihat bagian Facilities di bawah detail harga.'],
        'note': 'Fasilitas mengikuti data Room di database.',
    },
    {
        'slug': 'hotel-location',
        'title': 'How to find hotel location on maps?',
        'category': 'Hotel & Room',
        'intro': 'Lokasi hotel dapat dilihat di halaman Maps yang sudah memakai marker harga.',
        'steps': ['Buka detail room.', 'Klik Lihat Maps.', 'Geser peta atau cari hotel dari kolom search.'],
        'note': 'Marker harga memakai koordinat latitude dan longitude dari database.',
    },
    {
        'slug': 'guest-reviews',
        'title': 'How to view all guest reviews?',
        'category': 'Hotel & Room',
        'intro': 'Review tamu tersedia dari halaman detail room atau menu Reviews.',
        'steps': ['Pilih hotel dari halaman search.', 'Klik menu Reviews.', 'Baca komentar, rating, dan waktu review.'],
        'note': 'Review tersimpan pada tabel Review.',
    },
]


def seed(apps, schema_editor):
    Destination = apps.get_model('travel', 'Destination')
    Room = apps.get_model('travel', 'Room')
    Review = apps.get_model('travel', 'Review')
    HelpArticle = apps.get_model('travel', 'HelpArticle')
    destinations = {}
    for item in DESTINATIONS:
        destination, _ = Destination.objects.update_or_create(slug=item['slug'], defaults=item)
        destinations[item['slug']] = destination

    rooms = {}
    for item in ROOMS:
        data = item.copy()
        destination_slug = data.pop('destination')
        room, _ = Room.objects.update_or_create(
            slug=data['slug'],
            defaults={**data, 'destination': destinations[destination_slug], 'is_active': True},
        )
        rooms[room.slug] = room

    noah = rooms.get('noah-maratua-resort')
    if noah:
        for review in REVIEWS:
            Review.objects.get_or_create(room=noah, name=review['name'], text=review['text'], defaults=review)

    for item in HELP_ARTICLES:
        HelpArticle.objects.update_or_create(slug=item['slug'], defaults=item)


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
