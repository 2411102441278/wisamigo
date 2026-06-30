import logging
import os
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import JsonResponse

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except ImportError:
    genai = None

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if genai and GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    genai = None


def get_fallback_ai_response(message):
    q = (message or '').strip().lower()
    if 'bangkirai' in q or 'bukit' in q:
        return 'Bukit Bangkirai adalah destinasi wisata hutan dengan canopy walk, penginapan, dan pengalaman outdoor. Coba cari kamar resort atau eco-lodge di Wisamigo.'
    if 'derawan' in q:
        return 'Pulau Derawan terkenal dengan snorkeling, pantai pasir putih, dan tur penyu. Gunakan Wisamigo untuk menemukan hotel dekat laut dan aktivitas wisata.'
    if 'hotel' in q or 'kamar' in q or 'villa' in q:
        return 'Wisamigo menghadirkan pilihan hotel, villa, dan motel dengan harga jelas. Coba filter berdasarkan lokasi, tipe hotel, atau fasilitas yang kamu butuhkan.'
    if 'promo' in q or 'diskon' in q or 'harga' in q:
        return 'Cari penawaran terbaik dengan menggunakan filter harga dan kategori. Booking lebih awal untuk mendapatkan harga promosi dari Wisamigo.'
    if 'siapa' in q or 'nama' in q or 'kamu' in q:
        return 'Saya Wisamigo AI, asisten virtual yang membantu menjawab pertanyaan tentang destinasi dan akomodasi wisata.'
    return 'Maaf, AI eksternal tidak tersedia sekarang. Coba tanyakan destinasi populer seperti Bukit Bangkirai atau Pulau Derawan.'


def ai_chat(request):
    pesan = request.GET.get('message', '').strip()
    if not pesan:
        return JsonResponse({'reply': 'Silakan masukkan pertanyaan terlebih dahulu.'})

    reply = None
    if genai:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(pesan)
            reply = getattr(response, 'text', None)
            if not reply:
                reply = str(response)
        except Exception as exc:
            logger.exception('AI request failed')
            reply = None

    if not reply:
        reply = get_fallback_ai_response(pesan)

    return JsonResponse({'reply': reply})


from .models import Booking, Destination, HelpArticle, Payment, PaymentProof, Review, Room, UserProfile, format_rupiah


FILTER_CATEGORIES = ['City Hotel', 'Residental Hotel', 'Motel', 'Downtown Hotel', 'Resort Hotel']
FILTER_TYPES = ['All', 'Hostel', 'Villa']

PROFILE_DEFAULT = {
    'username': 'zulfiansyah',
    'email': 'zulfiansyah@gmail.com',
    'phone': '081273334444',
    'birth_date': '2012-12-12',
    'address': 'Samarinda, Sungai Dama',
}


def rupiah(number):
    return format_rupiah(number)


def safe_int(value, fallback=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def parse_date(value, fallback):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return fallback


def default_checkin():
    return date(2026, 7, 13)


def default_checkout():
    return date(2026, 7, 18)


def calendar_active_days(checkin_iso, checkout_iso):
    checkin_date = parse_date(checkin_iso, default_checkin())
    checkout_date = parse_date(checkout_iso, default_checkout())
    if checkout_date < checkin_date:
        checkout_date = checkin_date
    if checkin_date.year != 2026 or checkin_date.month != 7:
        return []
    last_day = 31
    start_day = max(checkin_date.day, 1)
    if checkout_date.year == 2026 and checkout_date.month == 7:
        end_day = min(checkout_date.day, last_day)
    else:
        end_day = start_day
    if end_day < start_day:
        end_day = start_day
    return list(range(start_day, end_day + 1))


def room_to_dict(room):
    return {
        'id': room.id,
        'slug': room.slug,
        'name': room.name,
        'destination': room.destination.name,
        'destination_slug': room.destination.slug,
        'location': room.location,
        'price': room.price,
        'price_number': room.price_number,
        'priceNumber': room.price_number,
        'image': room.image,
        'stars': room.stars,
        'badge': room.badge,
        'description': room.description,
        'features': room.feature_list,
        'category': room.category,
        'hotel_type': room.hotel_type,
        'capacity': room.capacity,
        'lat': room.latitude,
        'lng': room.longitude,
        'mapsUrl': f'https://www.google.com/maps/search/?api=1&query={room.latitude},{room.longitude}',
    }


def room_queryset():
    return Room.objects.select_related('destination').filter(is_active=True)


def get_room(slug):
    room = room_queryset().filter(slug=slug).first()
    if room:
        return room
    return room_queryset().first()


def get_destination(query=None):
    q = (query or '').strip()
    if q:
        destination = Destination.objects.filter(Q(name__icontains=q) | Q(slug__icontains=q.lower().replace(' ', '-'))).first()
        if destination:
            return destination
    return Destination.objects.filter(slug='pulau-derawan').first() or Destination.objects.first()


def build_booking_context(room, booking):
    room_data = room_to_dict(room) if isinstance(room, Room) else room

    if isinstance(booking, Booking):
        checkin = booking.checkin
        checkout = booking.checkout
        rooms_count = booking.rooms_count
        adults = booking.adults
        children = booking.children
        total = booking.total_price
        booking_code = booking.booking_code
    else:
        checkin = parse_date(booking.get('checkin'), default_checkin())
        checkout = parse_date(booking.get('checkout'), default_checkout())
        rooms_count = max(safe_int(booking.get('rooms', booking.get('rooms_count', 1)), 1), 1)
        adults = max(safe_int(booking.get('adults', 2), 2), 1)
        children = max(safe_int(booking.get('children', 0), 0), 0)
        total = room_data['price_number'] * rooms_count * max((checkout - checkin).days, 1)
        booking_code = booking.get('booking_code', 'WSM-2026')

    if checkout <= checkin:
        checkout = default_checkout()
    nights = max((checkout - checkin).days, 1)

    return {
        'room': room_data,
        'checkin': checkin,
        'checkout': checkout,
        'checkin_text': checkin.strftime('%d %B %Y'),
        'checkout_text': checkout.strftime('%d %B %Y'),
        'nights': nights,
        'rooms_count': rooms_count,
        'adults': adults,
        'children': children,
        'total': rupiah(total),
        'booking_code': booking_code,
    }


def get_profile_data(request):
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return {
            'username': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': profile.phone or PROFILE_DEFAULT['phone'],
            'birth_date': profile.birth_date or PROFILE_DEFAULT['birth_date'],
            'address': profile.address or PROFILE_DEFAULT['address'],
        }
    return {**PROFILE_DEFAULT, **request.session.get('profile_data', {})}


def build_map_room_data():
    return [room_to_dict(room) for room in room_queryset()]


def room_matches_map_query(room_data, query):
    q = (query or '').strip().lower()
    if not q:
        return True
    haystack = ' '.join([
        room_data.get('name', ''),
        room_data.get('destination', ''),
        room_data.get('location', ''),
        room_data.get('price', ''),
        str(room_data.get('price_number', '')),
        room_data.get('badge', ''),
    ]).lower()
    return q in haystack


def start_page(request):
    if request.user.is_authenticated:
        return redirect('travel:home')
    return render(request, 'travel/start.html')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('travel:home')
    error = ''
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        User = get_user_model()
        user_obj = User.objects.filter(email__iexact=email).first()
        username = user_obj.username if user_obj else email
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            return redirect(next_url or 'travel:home')
        error = 'Email atau password salah. Coba pakai akun yang sudah register.'
    return render(request, 'travel/login.html', {'error': error})


def register_page(request):
    if request.user.is_authenticated:
        return redirect('travel:home')
    error = ''
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not name or not email or not password:
            error = 'Nama, email, dan password wajib diisi.'
        elif get_user_model().objects.filter(email__iexact=email).exists():
            error = 'Email ini sudah terdaftar. Silakan login.'
        else:
            base_username = email.split('@')[0] or name.lower().replace(' ', '')
            username = base_username
            counter = 1
            User = get_user_model()
            while User.objects.filter(username=username).exists():
                counter += 1
                username = f'{base_username}{counter}'
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = name
            user.save(update_fields=['first_name'])
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            next_url = request.GET.get('next')
            return redirect(next_url or 'travel:home')
    return render(request, 'travel/register.html', {'error': error})


def logout_page(request):
    logout(request)
    return redirect('travel:start')


@login_required(login_url='travel:register')
def home_page(request):
    popular_destinations = []
    for destination in Destination.objects.exclude(slug='pulau-derawan')[:3]:
        popular_destinations.append({
            'title': destination.name,
            'query': destination.name,
            'image': destination.image,
        })
    quick_searches = list(Destination.objects.values_list('name', flat=True))
    room_gallery = [room_to_dict(room) for room in room_queryset()[:8]]
    context = {
        'popular_destinations': popular_destinations,
        'quick_searches': quick_searches,
        'room_gallery': room_gallery,
        'is_staff': request.user.is_staff,
    }
    return render(request, 'travel/home.html', context)


@login_required(login_url='travel:register')
def account_page(request):
    profile = get_profile_data(request)
    latest_bookings = []
    if request.user.is_authenticated:
        latest_bookings = Booking.objects.select_related('room').filter(user=request.user)[:3]
    account_menu = [
        {'title': 'Edit Profile', 'desc': 'Ubah data akun dan identitas kamu', 'icon': '👤', 'url_name': 'travel:edit_profile'},
        {'title': 'Change password', 'desc': 'Ubah password akun kamu', 'icon': '🔒', 'url_name': 'travel:forgot_password'},
        {'title': 'Payment', 'desc': 'Riwayat booking tersimpan di database', 'icon': '💳', 'url_name': 'travel:account_payment'},
        {'title': 'Help Center', 'desc': 'Pusat bantuan Wisamigo', 'icon': '💬', 'url_name': 'travel:help'},
        {'title': 'Setting', 'desc': 'Pengaturan akun dan notifikasi', 'icon': '⚙️'},
    ]
    return render(request, 'travel/account.html', {
        'account_menu': account_menu,
        'profile': profile,
        'latest_bookings': latest_bookings,
        'is_staff': request.user.is_staff,
    })


@login_required(login_url='travel:register')
def account_payment_page(request):
    latest_booking = Booking.objects.select_related('room').filter(user=request.user).order_by('-created_at').first()
    if latest_booking:
        return redirect('travel:payment', booking_code=latest_booking.booking_code)

    return render(request, 'travel/payment.html', {'no_booking': True})


def _admin_only_redirect(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Silakan login sebagai admin untuk mengakses dashboard ini.')
        return redirect('travel:login')
    if not request.user.is_staff:
        messages.warning(request, 'Akses ditolak. Hanya admin yang dapat membuka halaman ini.')
        return redirect('travel:home')
    return None


@login_required(login_url='travel:register')
def admin_payment_dashboard(request):
    admin_redirect = _admin_only_redirect(request)
    if admin_redirect:
        return admin_redirect

    query = request.GET.get('q', '').strip()
    proofs = PaymentProof.objects.select_related('payment__booking__user').order_by('-uploaded_at')
    if query:
        proofs = proofs.filter(
            Q(payment__booking__booking_code__icontains=query) |
            Q(payment__booking__user__email__icontains=query) |
            Q(payment__booking__user__username__icontains=query)
        )

    pending_count = proofs.filter(verification_status='pending').count()
    verified_count = proofs.filter(verification_status='verified').count()
    rejected_count = proofs.filter(verification_status='rejected').count()

    return render(request, 'travel/admin_payment_dashboard.html', {
        'proofs': proofs,
        'query': query,
        'pending_count': pending_count,
        'verified_count': verified_count,
        'rejected_count': rejected_count,
    })


@login_required(login_url='travel:register')
def admin_verify_payment_proof(request, proof_id):
    admin_redirect = _admin_only_redirect(request)
    if admin_redirect:
        return admin_redirect

    proof = get_object_or_404(PaymentProof, pk=proof_id)
    proof.is_verified = True
    proof.verification_status = 'verified'
    proof.verified_at = datetime.now()
    proof.admin_notes = ''
    proof.save()

    payment = proof.payment
    payment.status = 'paid'
    payment.save()

    messages.success(request, f'Bukti pembayaran {proof.payment.booking.booking_code} berhasil diverifikasi.')
    return redirect('travel:admin_payment_dashboard')


@login_required(login_url='travel:register')
def admin_reject_payment_proof(request, proof_id):
    admin_redirect = _admin_only_redirect(request)
    if admin_redirect:
        return admin_redirect

    proof = get_object_or_404(PaymentProof, pk=proof_id)
    proof.is_verified = False
    proof.verification_status = 'rejected'
    proof.verified_at = None
    proof.save()

    payment = proof.payment
    payment.status = 'cancelled'
    payment.save()

    messages.warning(request, f'Bukti pembayaran {proof.payment.booking.booking_code} ditolak.')
    return redirect('travel:admin_payment_dashboard')


@login_required(login_url='travel:register')
def admin_payment_proof_detail(request, proof_id):
    admin_redirect = _admin_only_redirect(request)
    if admin_redirect:
        return admin_redirect

    proof = get_object_or_404(
        PaymentProof.objects.select_related('payment__booking__user'),
        pk=proof_id
    )

    return render(request, 'travel/admin_payment_proof_detail.html', {
        'proof': proof,
    })


@login_required(login_url='travel:register')
def admin_add_payment_proof(request):
    admin_redirect = _admin_only_redirect(request)
    if admin_redirect:
        return admin_redirect

    if request.method != 'POST':
        return redirect('travel:admin_payment_dashboard')

    booking_code = request.POST.get('booking_code', '').strip()
    if not booking_code:
        messages.error(request, 'Masukkan kode booking untuk upload bukti pembayaran.')
        return redirect('travel:admin_payment_dashboard')

    try:
        booking = Booking.objects.get(booking_code=booking_code)
    except Booking.DoesNotExist:
        messages.error(request, 'Booking tidak ditemukan untuk kode yang dimasukkan.')
        return redirect('travel:admin_payment_dashboard')

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_price,
            'status': 'pending',
            'transaction_id': f"WSM-{uuid.uuid4().hex[:12].upper()}",
        }
    )

    if 'proof_image' not in request.FILES:
        messages.error(request, 'Pilih file gambar terlebih dahulu.')
        return redirect('travel:admin_payment_dashboard')

    proof_image = request.FILES['proof_image']
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    file_ext = proof_image.name.split('.')[-1].lower()
    if file_ext not in valid_extensions:
        messages.error(request, 'Format file tidak didukung. Gunakan JPG, PNG, GIF, atau WebP.')
        return redirect('travel:admin_payment_dashboard')

    if proof_image.size > 5 * 1024 * 1024:
        messages.error(request, 'Ukuran file terlalu besar. Maksimal 5MB.')
        return redirect('travel:admin_payment_dashboard')

    proof, created = PaymentProof.objects.get_or_create(
        payment=payment,
        defaults={'image': proof_image}
    )
    if not created:
        proof.image = proof_image
        proof.verification_status = 'pending'
        proof.is_verified = False
        proof.admin_notes = ''
        proof.verified_at = None
        proof.save()

    messages.success(request, f'Bukti pembayaran untuk booking {booking_code} berhasil diunggah.')
    return redirect('travel:admin_payment_dashboard')


@login_required(login_url='travel:register')
def edit_profile_page(request):
    profile = get_profile_data(request)
    saved = False
    if request.method == 'POST':
        profile = {
            'username': request.POST.get('username', profile['username']).strip() or PROFILE_DEFAULT['username'],
            'email': request.POST.get('email', profile['email']).strip() or PROFILE_DEFAULT['email'],
            'phone': request.POST.get('phone', profile['phone']).strip() or PROFILE_DEFAULT['phone'],
            'birth_date': request.POST.get('birth_date', profile['birth_date']).strip() or PROFILE_DEFAULT['birth_date'],
            'address': request.POST.get('address', profile['address']).strip() or PROFILE_DEFAULT['address'],
        }
        if request.user.is_authenticated:
            user = request.user
            user.first_name = profile['username']
            user.email = profile['email']
            user.save(update_fields=['first_name', 'email'])
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.phone = profile['phone']
            user_profile.birth_date = profile['birth_date']
            user_profile.address = profile['address']
            user_profile.save()
        else:
            request.session['profile_data'] = profile
        saved = True
    return render(request, 'travel/edit_profile.html', {'profile': profile, 'saved': saved})


def filter_rooms(query='', min_price=300000, max_price=2500000, categories=None, persons=1, hotel_type='All'):
    categories = categories or []
    rooms = room_queryset().filter(price_number__gte=min_price, price_number__lte=max_price, capacity__gte=persons)
    q = (query or '').strip()
    if q:
        rooms = rooms.filter(
            Q(name__icontains=q) |
            Q(destination__name__icontains=q) |
            Q(location__icontains=q) |
            Q(badge__icontains=q) |
            Q(category__icontains=q) |
            Q(hotel_type__icontains=q)
        )
    if categories:
        rooms = rooms.filter(category__in=categories)
    if hotel_type and hotel_type != 'All':
        rooms = rooms.filter(hotel_type=hotel_type)
    return [room_to_dict(room) for room in rooms]


@login_required(login_url='travel:register')
def search_page(request):
    query = request.GET.get('q', 'Pulau Derawan')
    destination = get_destination(query)
    if not destination:
        return render(request, 'travel/search.html', {'query': query, 'deals': [], 'all_destinations': []})
    deals = [room_to_dict(room) for room in destination.rooms.filter(is_active=True)]
    result = {
        'label': destination.name,
        'hero': destination.hero_image,
        'subtitle': destination.subtitle,
    }
    context = {
        'query': destination.name,
        'result_key': destination.slug,
        'result': result,
        'deals': deals,
        'all_destinations': list(Destination.objects.values_list('name', flat=True)),
    }
    return render(request, 'travel/search.html', context)


@login_required(login_url='travel:register')
def filter_page(request):
    query = request.GET.get('q', '')
    min_price = safe_int(request.GET.get('min_price'), 300000)
    max_price = safe_int(request.GET.get('max_price'), 2500000)
    if min_price > max_price:
        min_price, max_price = max_price, min_price
    categories = request.GET.getlist('category')
    persons = max(safe_int(request.GET.get('persons'), 1), 1)
    hotel_type = request.GET.get('hotel_type', 'All')
    if hotel_type not in FILTER_TYPES:
        hotel_type = 'All'

    results = filter_rooms(query, min_price, max_price, categories, persons, hotel_type)
    context = {
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'min_price_label': rupiah(min_price),
        'max_price_label': rupiah(max_price),
        'categories': FILTER_CATEGORIES,
        'selected_categories': categories,
        'persons': persons,
        'hotel_types': FILTER_TYPES,
        'hotel_type': hotel_type,
        'results': results,
        'result_count': len(results),
        'all_destinations': list(Destination.objects.values_list('name', flat=True)),
    }
    return render(request, 'travel/filter.html', context)


@login_required(login_url='travel:register')
def room_detail_page(request, slug):
    room = get_room(slug)
    if not room:
        return redirect('travel:home')
    similar_rooms = [room_to_dict(item) for item in room_queryset().filter(destination=room.destination).exclude(slug=room.slug)[:3]]
    context = {
        'room': room_to_dict(room),
        'similar_rooms': similar_rooms,
    }
    return render(request, 'travel/room_detail.html', context)


@login_required(login_url='travel:register')
def booking_dates_page(request, slug):
    room = get_room(slug)
    if not room:
        return redirect('travel:home')
    pending = request.session.get('pending_booking', {})
    checkin = pending.get('checkin', default_checkin().isoformat())
    checkout = pending.get('checkout', default_checkout().isoformat())

    if request.method == 'POST':
        selected_checkin = request.POST.get('checkin') or checkin
        selected_checkout = request.POST.get('checkout') or checkout
        request.session['pending_booking'] = {
            'slug': room.slug,
            'checkin': selected_checkin,
            'checkout': selected_checkout,
        }
        return redirect('travel:booking_rooms', slug=room.slug)

    context = {
        'room': room_to_dict(room),
        'checkin': checkin,
        'checkout': checkout,
        'calendar_days': list(range(1, 32)),
        'active_days': calendar_active_days(checkin, checkout),
        'calendar_month': '2026-07',
    }
    return render(request, 'travel/booking_dates.html', context)


@login_required(login_url='travel:register')
def booking_rooms_page(request, slug):
    room = get_room(slug)
    if not room:
        return redirect('travel:home')
    pending = request.session.get('pending_booking', {})
    if pending.get('slug') != room.slug:
        pending = {
            'slug': room.slug,
            'checkin': default_checkin().isoformat(),
            'checkout': default_checkout().isoformat(),
        }
        request.session['pending_booking'] = pending

    if request.method == 'POST':
        rooms_count = max(safe_int(request.POST.get('rooms'), 1), 1)
        adults = max(safe_int(request.POST.get('adults'), 2), 1)
        children = max(safe_int(request.POST.get('children'), 0), 0)
        checkin = parse_date(pending.get('checkin'), default_checkin())
        checkout = parse_date(pending.get('checkout'), default_checkout())
        if checkout <= checkin:
            checkout = default_checkout()
        nights = max((checkout - checkin).days, 1)
        total = room.price_number * rooms_count * nights
        booking_code = 'WSM-' + datetime.now().strftime('%y%m%d%H%M%S')
        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            room=room,
            booking_code=booking_code,
            checkin=checkin,
            checkout=checkout,
            rooms_count=rooms_count,
            adults=adults,
            children=children,
            total_price=total,
            status='pending',
        )
        request.session['last_booking_id'] = booking.id
        request.session['last_booking'] = {
            **pending,
            'rooms': rooms_count,
            'adults': adults,
            'children': children,
            'booking_code': booking_code,
        }
        # Redirect to payment page so user completes payment before final confirmation
        return redirect('travel:payment', booking_code=booking.booking_code)

    context = build_booking_context(room, {**pending, 'rooms': 1, 'adults': 2, 'children': 0})
    return render(request, 'travel/booking_rooms.html', context)


@login_required(login_url='travel:register')
def booking_payment_page(request, slug):
    room = get_room(slug)
    if not room:
        return redirect('travel:home')

    booking = Booking.objects.select_related('room').filter(user=request.user, room=room).order_by('-created_at').first()
    if not booking:
        messages.error(request, 'Tidak ada booking terbaru untuk room ini. Silakan buat booking terlebih dahulu.')
        return redirect('travel:room_detail', slug=room.slug)

    return redirect('travel:payment', booking_code=booking.booking_code)


@login_required(login_url='travel:register')
def booking_success_page(request, slug):
    room = get_room(slug)
    if not room:
        return redirect('travel:home')

    booking = None
    booking_id = request.session.get('last_booking_id')
    if booking_id:
        booking = Booking.objects.select_related('room').filter(id=booking_id, room=room).first()

    if booking:
        payment = getattr(booking, 'payment', None)
        context = build_booking_context(room, booking)
        context['payment'] = payment
        context['payment_status'] = payment.status if payment else 'pending'
        context['payment_url'] = reverse('travel:payment', kwargs={'booking_code': booking.booking_code})
    else:
        last_booking = request.session.get('last_booking') or {
            'slug': room.slug,
            'checkin': default_checkin().isoformat(),
            'checkout': default_checkout().isoformat(),
            'rooms': 1,
            'adults': 2,
            'children': 0,
            'booking_code': 'WSM-DEMO',
        }
        context = build_booking_context(room, last_booking)
        context['payment'] = None
        context['payment_status'] = 'pending'
        context['payment_url'] = reverse('travel:booking_payment', kwargs={'slug': room.slug})
    return render(request, 'travel/booking_success.html', context)


@login_required(login_url='travel:register')
def maps_page(request, slug=None):
    map_query = (request.GET.get('q') or '').strip()
    map_rooms = build_map_room_data()
    matched_rooms = [item for item in map_rooms if room_matches_map_query(item, map_query)]

    if map_query and matched_rooms:
        room_data = matched_rooms[0]
    else:
        selected_room = get_room(slug) if slug else room_queryset().first()
        room_data = room_to_dict(selected_room) if selected_room else (map_rooms[0] if map_rooms else {})

    if slug and not map_query:
        selected_room = get_room(slug)
        if selected_room:
            room_data = room_to_dict(selected_room)

    context = {
        'room': room_data,
        'rooms': [room_to_dict(room) for room in room_queryset()],
        'map_rooms': map_rooms,
        'map_query': map_query,
        'selected_slug': room_data.get('slug', ''),
        'matched_count': len(matched_rooms) if map_query else len(map_rooms),
    }
    return render(request, 'travel/maps.html', context)


@login_required(login_url='travel:register')
def reviews_page(request, slug=None):
    room = get_room(slug) if slug else room_queryset().first()
    if not room:
        return redirect('travel:home')
    room_reviews = Review.objects.filter(Q(room=room) | Q(room__isnull=True))[:20]
    total_reviews = room.reviews.count() or room_reviews.count() or 0
    if total_reviews:
        ratings = [item.rating for item in room_reviews]
        average_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    else:
        average_rating = 0
    context = {
        'room': room_to_dict(room),
        'reviews': room_reviews,
        'total_reviews': total_reviews if total_reviews >= 5 else 33,
        'average_rating': average_rating or '4.8',
    }
    return render(request, 'travel/reviews.html', context)


def forgot_password_page(request):
    sent = False
    if request.method == 'POST':
        sent = True
    return render(request, 'travel/forgot_password.html', {'sent': sent})


@login_required(login_url='travel:register')
def help_page(request):
    query = request.GET.get('q', '').strip()
    articles = HelpArticle.objects.all()
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(category__icontains=query) | Q(intro__icontains=query))

    grouped = {}
    for article in articles:
        grouped.setdefault(article.category, []).append({'title': article.title, 'slug': article.slug})

    filtered_faqs = [{'category': category, 'items': items} for category, items in grouped.items()]
    context = {
        'query': query,
        'faqs': filtered_faqs,
        'total_found': sum(len(group['items']) for group in filtered_faqs),
    }
    return render(request, 'travel/help.html', context)


@login_required(login_url='travel:register')
def help_article_page(request, slug):
    article = HelpArticle.objects.filter(slug=slug).first() or HelpArticle.objects.first()
    if not article:
        return redirect('travel:help')
    article_data = {
        'title': article.title,
        'category': article.category,
        'intro': article.intro,
        'steps': article.steps,
        'note': article.note,
    }
    related = [
        {'title': item.title, 'slug': item.slug}
        for item in HelpArticle.objects.filter(category=article.category).exclude(slug=article.slug)[:4]
    ]
    return render(request, 'travel/help_detail.html', {'article': article_data, 'related': related})

def ai_page(request):
    return render(request, 'travel/ai.html')


# Payment Views
from .models import Payment
import uuid

def payment_page(request, booking_code):
    """Display payment page for a booking"""
    try:
        booking = Booking.objects.get(booking_code=booking_code)
    except Booking.DoesNotExist:
        messages.error(request, 'Booking tidak ditemukan')
        return redirect('travel:home')

    # If booking is already confirmed, redirect to success page
    if booking.status == 'confirmed':
        return redirect('travel:booking_success', slug=booking.room.slug)

    # Check if payment already exists, otherwise create it safely
    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_price,
            'status': 'pending',
            'transaction_id': f"WSM-{uuid.uuid4().hex[:12].upper()}",
        }
    )

    context = {
        'booking': booking,
        'payment': payment,
        'profile': get_profile_data(request),
        'payment_methods': [
            {'value': 'bca_va', 'label': 'BCA Virtual Account'},
            {'value': 'mandiri_va', 'label': 'Mandiri Virtual Account'},
            {'value': 'bri_va', 'label': 'BRI Virtual Account'},
        ],
    }
    return render(request, 'travel/payment.html', context)


def process_payment(request, booking_code):
    """Process payment confirmation after proof is verified"""
    if request.method != 'POST':
        return redirect('travel:payment', booking_code=booking_code)
    
    try:
        booking = Booking.objects.get(booking_code=booking_code)
    except Booking.DoesNotExist:
        messages.error(request, 'Booking tidak ditemukan')
        return redirect('travel:home')
    
    # Get payment
    payment = Payment.objects.filter(booking=booking).first()
    if not payment:
        messages.error(request, 'Data pembayaran tidak ditemukan')
        return redirect('travel:payment', booking_code=booking_code)
    
    # Check if payment has verified proof
    if not payment.has_verified_proof:
        messages.error(request, 'Bukti pembayaran Anda belum diverifikasi oleh admin. Silakan tunggu atau hubungi support.')
        return redirect('travel:payment', booking_code=booking_code)
    
    # Update payment details
    if not payment.transaction_id:
        payment.transaction_id = f"WSM-{uuid.uuid4().hex[:12].upper()}"
    payment.status = 'paid'
    payment.save()
    
    # Update booking status to confirmed
    booking.status = 'confirmed'
    booking.save()
    
    # After payment, redirect to booking success page for the room
    try:
        return redirect('travel:booking_success', slug=booking.room.slug)
    except Exception:
        return redirect('travel:payment_success', booking_code=booking_code)


def upload_payment_proof(request, booking_code):
    """Handle payment proof upload"""
    if request.method != 'POST':
        return redirect('travel:payment', booking_code=booking_code)
    
    try:
        booking = Booking.objects.get(booking_code=booking_code)
    except Booking.DoesNotExist:
        messages.error(request, 'Booking tidak ditemukan')
        return redirect('travel:home')

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.total_price,
            'status': 'pending',
            'transaction_id': f"WSM-{uuid.uuid4().hex[:12].upper()}",
        }
    )

    if 'proof_image' not in request.FILES:
        messages.error(request, 'Pilih file gambar terlebih dahulu')
        return redirect('travel:payment', booking_code=booking_code)

    proof_image = request.FILES['proof_image']
    
    # Validate file type
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    file_ext = proof_image.name.split('.')[-1].lower()
    
    if file_ext not in valid_extensions:
        messages.error(request, 'Format file tidak didukung. Gunakan JPG, PNG, GIF, atau WebP')
        return redirect('travel:payment', booking_code=booking_code)
    
    # Validate file size (max 5MB)
    if proof_image.size > 5 * 1024 * 1024:
        messages.error(request, 'Ukuran file terlalu besar. Maksimal 5MB')
        return redirect('travel:payment', booking_code=booking_code)
    
    # Import PaymentProof here to avoid circular imports
    from .models import PaymentProof
    
    # Create or update proof
    proof, created = PaymentProof.objects.get_or_create(
        payment=payment,
        defaults={'image': proof_image}
    )
    
    if not created:
        proof.image = proof_image
        proof.verification_status = 'pending'
        proof.is_verified = False
        proof.admin_notes = ''
        proof.verified_at = None
        proof.save()
    
    messages.success(request, 'Bukti pembayaran berhasil diunggah. Admin akan memverifikasi dalam waktu singkat.')
    return redirect('travel:payment', booking_code=booking_code)


def payment_success(request, booking_code):
    """Display payment success page"""
    try:
        booking = Booking.objects.get(booking_code=booking_code)
        payment = booking.payment
    except (Booking.DoesNotExist, Payment.DoesNotExist):
        messages.error(request, 'Data pembayaran tidak ditemukan')
        return redirect('travel:home')
    
    context = {
        'booking': booking,
        'payment': payment,
        'profile': get_profile_data(request),
    }
    return render(request, 'travel/payment_success.html', context)


def payment_history(request):
    """Display user's payment history"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Silakan login terlebih dahulu')
        return redirect('travel:login')
    
    payments = Payment.objects.filter(booking__user=request.user).select_related('booking__room')
    bookings = Booking.objects.filter(user=request.user).select_related('room')
    
    context = {
        'payments': payments,
        'bookings': bookings,
        'profile': get_profile_data(request),
    }
    return render(request, 'travel/payment_history.html', context)