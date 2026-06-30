from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

def format_rupiah(number):
    return 'Rp {:,}'.format(int(number or 0)).replace(',', '.')


class Destination(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=160, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    hero_image = models.CharField(max_length=160, default='travel/img/ocean-hero.svg')
    image = models.CharField(max_length=160, default='travel/img/beach-card.svg')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    CATEGORY_CHOICES = [
        ('City Hotel', 'City Hotel'),
        ('Residental Hotel', 'Residental Hotel'),
        ('Motel', 'Motel'),
        ('Downtown Hotel', 'Downtown Hotel'),
        ('Resort Hotel', 'Resort Hotel'),
    ]
    HOTEL_TYPE_CHOICES = [
        ('All', 'All'),
        ('Hostel', 'Hostel'),
        ('Villa', 'Villa'),
    ]

    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='rooms')
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=180)
    price_number = models.PositiveIntegerField(default=0)
    image = models.CharField(max_length=160, default='travel/img/resort-derawan.svg')
    stars = models.PositiveSmallIntegerField(default=5)
    badge = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='Resort Hotel')
    hotel_type = models.CharField(max_length=30, choices=HOTEL_TYPE_CHOICES, default='All')
    capacity = models.PositiveSmallIntegerField(default=2)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['destination__name', 'price_number']

    def __str__(self):
        return self.name

    @property
    def price(self):
        return format_rupiah(self.price_number)

    @property
    def feature_list(self):
        if isinstance(self.features, list):
            return self.features
        return []


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=30, blank=True)
    birth_date = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    favorite_destination = models.ForeignKey(Destination, null=True, blank=True, on_delete=models.SET_NULL)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    booking_code = models.CharField(max_length=30, unique=True)
    checkin = models.DateField()
    checkout = models.DateField()
    rooms_count = models.PositiveSmallIntegerField(default=1)
    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking_code} - {self.room.name}'

    @property
    def total_price_rupiah(self):
        return format_rupiah(self.total_price)

    @property
    def nights(self):
        return max((self.checkout - self.checkin).days, 1)

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('cancelled', 'Cancelled'),
]


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bca_va', 'BCA Virtual Account'),
        ('mandiri_va', 'Mandiri Virtual Account'),
        ('bri_va', 'BRI Virtual Account'),
        ('bank_transfer', 'Bank Transfer'),
        ('gopay', 'GoPay'),
        ('ovo', 'OVO'),
        ('e_wallet', 'E-Wallet'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.id} - {self.booking.booking_code} - {self.status}'

    @property
    def amount_rupiah(self):
        return format_rupiah(self.amount)

    @property
    def is_paid(self):
        return self.status == 'paid'

    @property
    def has_proof(self):
        return self.proof.exists()

    @property
    def is_verified(self):
        return self.proof.filter(verification_status='verified').exists()

    @property
    def has_verified_proof(self):
        """Check if payment has verified proof"""
        return self.proof.filter(verification_status='verified').exists()


class PaymentProof(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='proof')
    image = models.ImageField(upload_to='payment_proofs/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Proof {self.id} - Payment {self.payment.id} - {self.verification_status}'



class Review(models.Model):
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=120)
    avatar = models.CharField(max_length=10, default='US')
    time = models.CharField(max_length=80, default='Baru saja')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.rating}'


class HelpArticle(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    category = models.CharField(max_length=100)
    intro = models.TextField(blank=True)
    steps = models.JSONField(default=list, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return self.title
