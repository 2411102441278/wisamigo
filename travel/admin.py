from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_protect
from .models import Payment, PaymentProof
from django.utils.safestring import mark_safe
import uuid

class WisamigoAdminSite(AdminSite):
    site_header = 'Wisamigo Admin'
    site_title = 'Wisamigo Admin'
    index_title = 'Admin Payment Verification'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('payment-dashboard/', self.admin_view(self.payment_dashboard_view), name='payment-dashboard'),
            path('payment-proof/upload/', self.admin_view(csrf_protect(self.admin_add_payment_proof)), name='paymentproof-upload'),
            path('payment-proof/<int:proof_id>/verify/', self.admin_view(self.verify_proof_view), name='paymentproof-verify'),
            path('payment-proof/<int:proof_id>/reject/', self.admin_view(self.reject_proof_view), name='paymentproof-reject'),
        ]
        return custom_urls + urls

    def payment_dashboard_view(self, request):
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

        context = {
            **self.each_context(request),
            'proofs': proofs,
            'query': query,
            'pending_count': pending_count,
            'verified_count': verified_count,
            'rejected_count': rejected_count,
        }
        return render(request, 'travel/admin_payment_dashboard.html', context)

    def admin_add_payment_proof(self, request):
        if request.method != 'POST':
            return redirect('admin:payment-dashboard')

        booking_code = request.POST.get('booking_code', '').strip()
        if not booking_code:
            messages.error(request, 'Masukkan kode booking untuk upload bukti pembayaran.')
            return redirect('admin:payment-dashboard')

        from .models import Booking, Payment

        try:
            booking = Booking.objects.get(booking_code=booking_code)
        except Booking.DoesNotExist:
            messages.error(request, 'Booking tidak ditemukan untuk kode yang dimasukkan.')
            return redirect('admin:payment-dashboard')

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
            return redirect('admin:payment-dashboard')

        proof_image = request.FILES['proof_image']
        valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        file_ext = proof_image.name.split('.')[-1].lower()
        if file_ext not in valid_extensions:
            messages.error(request, 'Format file tidak didukung. Gunakan JPG, PNG, GIF, atau WebP.')
            return redirect('admin:payment-dashboard')

        if proof_image.size > 5 * 1024 * 1024:
            messages.error(request, 'Ukuran file terlalu besar. Maksimal 5MB.')
            return redirect('admin:payment-dashboard')

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
        return redirect('admin:payment-dashboard')

    def verify_proof_view(self, request, proof_id):
        proof = get_object_or_404(PaymentProof, pk=proof_id)
        proof.is_verified = True
        proof.verification_status = 'verified'
        proof.verified_at = timezone.now()
        proof.admin_notes = ''
        proof.save()

        payment = proof.payment
        payment.status = 'paid'
        payment.save()

        messages.success(request, f'Bukti pembayaran {proof.payment.booking.booking_code} berhasil diverifikasi.')
        return redirect('admin:payment-dashboard')

    def reject_proof_view(self, request, proof_id):
        proof = get_object_or_404(PaymentProof, pk=proof_id)
        proof.is_verified = False
        proof.verification_status = 'rejected'
        proof.verified_at = None
        proof.save()

        payment = proof.payment
        payment.status = 'pending'
        payment.save()

        messages.warning(request, f'Bukti pembayaran {proof.payment.booking.booking_code} ditolak.')
        return redirect('admin:payment-dashboard')


admin_site = WisamigoAdminSite(name='admin')


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'booking', 'amount_rupiah', 'status',
        'payment_method', 'verified_badge', 'created_at'
    )
    list_filter = ('status', 'payment_method')
    search_fields = ('booking__booking_code', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')

    def verified_badge(self, obj):
        if obj.proof.filter(verification_status='verified').exists():
            return mark_safe('<span style="color:green;font-weight:600;">✓ Diverifikasi</span>')
        elif obj.proof.filter(verification_status='rejected').exists():
            return mark_safe('<span style="color:red;font-weight:600;">✗ Ditolak</span>')
        return mark_safe('<span style="color:#f57f17;font-weight:600;">⏱ Pending</span>')
    verified_badge.short_description = 'Status'


class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_info', 'image_preview', 'verification_status', 'uploaded_at', 'aksi')
    list_filter = ('verification_status',)
    search_fields = ('payment__booking__booking_code',)
    readonly_fields = ('image_preview_large', 'uploaded_at')
    fields = ('payment', 'image', 'image_preview_large', 'verification_status',
              'is_verified', 'admin_notes', 'verified_at', 'uploaded_at')

    def booking_info(self, obj):
        booking = obj.payment.booking
        return f'{booking.booking_code} ({obj.payment.amount_rupiah})'
    booking_info.short_description = 'Booking'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px;border-radius:4px;" />', obj.image.url)
        return 'Belum ada gambar'
    image_preview.short_description = 'Bukti Pembayaran'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:400px;border-radius:6px;" />', obj.image.url)
        return 'Belum ada gambar'
    image_preview_large.short_description = 'Preview Bukti Pembayaran'

    def aksi(self, obj):
        if obj.verification_status == 'verified':
            return format_html('<span style="color:#2e7d32;font-weight:600;">✓ Terverifikasi</span>')
        if obj.verification_status == 'rejected':
            return format_html('<span style="color:#d32f2f;font-weight:600;">✗ Ditolak</span>')

        verify_url = reverse('admin:travel_paymentproof_verify', args=[obj.pk])
        reject_url = reverse('admin:travel_paymentproof_reject', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background:#2e7d32;color:#fff;padding:5px 12px;'
            'border-radius:4px;margin-right:6px;text-decoration:none;font-size:12px;font-weight:600;">'
            '✓ Verifikasi</a>'
            '<a class="button" href="{}" style="background:#d32f2f;color:#fff;padding:5px 12px;'
            'border-radius:4px;text-decoration:none;font-size:12px;font-weight:600;">'
            '✗ Tolak</a>',
            verify_url, reject_url,
        )
    aksi.short_description = 'Aksi Verifikasi'

    def get_urls(self):
        custom_urls = [
            path('<int:proof_id>/verify/', self.admin_site.admin_view(self.verify_proof), name='travel_paymentproof_verify'),
            path('<int:proof_id>/reject/', self.admin_site.admin_view(self.reject_proof), name='travel_paymentproof_reject'),
        ]
        return custom_urls + super().get_urls()

    def verify_proof(self, request, proof_id):
        proof = get_object_or_404(PaymentProof, pk=proof_id)
        proof.is_verified = True
        proof.verification_status = 'verified'
        proof.verified_at = timezone.now()
        proof.admin_notes = ''
        proof.save()

        # sinkronisasi ke Payment
        payment = proof.payment
        payment.status = 'paid'
        payment.save()

        self.message_user(
            request,
            f"Bukti pembayaran #{proof.id} ({proof.payment.booking.booking_code}) berhasil diverifikasi.",
            level=messages.SUCCESS,
        )
        return redirect('admin:travel_paymentproof_changelist')

    def reject_proof(self, request, proof_id):
        proof = get_object_or_404(PaymentProof, pk=proof_id)
        proof.is_verified = False
        proof.verification_status = 'rejected'
        proof.verified_at = None
        proof.save()

        # sinkronisasi ke Payment
        payment = proof.payment
        payment.status = 'pending'  # atau 'cancelled' sesuai kebutuhan
        payment.save()

        self.message_user(
            request,
            f'Bukti pembayaran #{proof.id} ({proof.payment.booking.booking_code}) ditolak.',
            level=messages.WARNING,
        )
        return redirect('admin:travel_paymentproof_changelist')


admin_site.register(Payment, PaymentAdmin)
admin_site.register(PaymentProof, PaymentProofAdmin)
