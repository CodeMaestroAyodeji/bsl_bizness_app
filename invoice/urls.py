from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/new/', views.vendor_create, name='vendor_create'),
    re_path(r'^vendors/(?P<pk>[0-9a-f]{24})/$', views.vendor_detail, name='vendor_detail'),
    re_path(r'^vendors/(?P<pk>[0-9a-f]{24})/edit/$', views.vendor_update, name='vendor_update'),
    re_path(r'^vendors/(?P<pk>[0-9a-f]{24})/delete/$', views.vendor_delete, name='vendor_delete'),
    re_path(r'^vendors/(?P<pk>[0-9a-f]{24})/logo/$', views.vendor_logo, name='vendor_logo'),

    path('settings/', views.client_settings, name='client_settings'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit_role/', views.user_edit_role, name='user_edit_role'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/bulk_download/', views.invoice_bulk_download, name='invoice_bulk_download'),
    re_path(r'^invoices/(?P<pk>[0-9a-f]{24})/$', views.invoice_detail, name='invoice_detail'),
    re_path(r'^invoices/(?P<pk>[0-9a-f]{24})/edit/$', views.invoice_update, name='invoice_update'),
    re_path(r'^invoices/(?P<pk>[0-9a-f]{24})/delete/$', views.invoice_delete, name='invoice_delete'),
    re_path(r'^invoices/(?P<pk>[0-9a-f]{24})/print/$', views.invoice_print_preview, name='invoice_print_preview'),

    # Purchase Order URLs
    path('purchase-orders/', views.po_list, name='po_list'),
    path('purchase-orders/new/', views.po_create, name='po_create'),
    path('purchase-orders/<str:pk>/', views.po_detail, name='po_detail'),
    path('purchase-orders/<str:pk>/edit/', views.po_update, name='po_update'),
    path('purchase-orders/<str:pk>/delete/', views.po_delete, name='po_delete'),
    path('purchase-orders/<str:pk>/download/', views.po_download, name='po_download'),
    path('purchase-orders/bulk_download/', views.po_bulk_download, name='po_bulk_download'),
]