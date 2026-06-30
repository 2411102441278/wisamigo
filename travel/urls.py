from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('', views.start_page, name='start'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('home/', views.home_page, name='home'),
    path('account/', views.account_page, name='account'),
    path('account/edit/', views.edit_profile_page, name='edit_profile'),
    path('search/', views.search_page, name='search'),
    path('filter/', views.filter_page, name='filter'),
    path('room/<slug:slug>/', views.room_detail_page, name='room_detail'),
    path('booking/<slug:slug>/dates/', views.booking_dates_page, name='booking_dates'),
    path('booking/<slug:slug>/rooms/', views.booking_rooms_page, name='booking_rooms'),
    path('booking/<slug:slug>/payment/', views.booking_payment_page, name='booking_payment'),
    path('booking/<slug:slug>/success/', views.booking_success_page, name='booking_success'),
    path('account/payment/', views.account_payment_page, name='account_payment'),
    path('maps/', views.maps_page, name='maps'),
    path('maps/<slug:slug>/', views.maps_page, name='maps_room'),
    path('reviews/', views.reviews_page, name='reviews'),
    path('reviews/<slug:slug>/', views.reviews_page, name='reviews_room'),
    path('forgot-password/', views.forgot_password_page, name='forgot_password'),
    path('help/', views.help_page, name='help'),
    path('help/<slug:slug>/', views.help_article_page, name='help_article'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('ai/', views.ai_page, name='ai_page'),
    
    # App admin dashboard URLs
    path('admin-dashboard/', views.admin_payment_dashboard, name='admin_payment_dashboard'),
    path('admin-dashboard/upload-proof/', views.admin_add_payment_proof, name='admin_add_payment_proof'),
    path('admin-dashboard/proof/<int:proof_id>/verify/', views.admin_verify_payment_proof, name='admin_verify_payment_proof'),
    path('admin-dashboard/proof/<int:proof_id>/reject/', views.admin_reject_payment_proof, name='admin_reject_payment_proof'),
    path('admin-dashboard/proof/<int:proof_id>/', views.admin_payment_proof_detail, name='admin_payment_proof_detail'),
    
    # Payment URLs
    path('payment/<str:booking_code>/', views.payment_page, name='payment'),
    path('payment/<str:booking_code>/process/', views.process_payment, name='process_payment'),
    path('payment/<str:booking_code>/upload-proof/', views.upload_payment_proof, name='upload_payment_proof'),
    path('payment/<str:booking_code>/success/', views.payment_success, name='payment_success'),
    path('payment-history/', views.payment_history, name='payment_history'),
]
