from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/new/', views.vendor_create, name='vendor_create'),
    path('vendors/<str:pk>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/<str:pk>/edit/', views.vendor_update, name='vendor_update'),
    path('vendors/<str:pk>/delete/', views.vendor_delete, name='vendor_delete'),

    path('settings/', views.client_settings, name='client_settings'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit_role/', views.user_edit_role, name='user_edit_role'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<str:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<str:pk>/edit/', views.invoice_update, name='invoice_update'),
    path('invoices/<str:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<str:pk>/print/', views.invoice_print_preview, name='invoice_print_preview'),
    path('invoices/bulk_download/', views.invoice_bulk_download, name='invoice_bulk_download'),
]
