from django.urls import path
from . import views

urlpatterns = [
    path('', views.gatepass_list, name='gatepass_list'),
    path('<int:pk>/', views.gatepass_detail, name='gatepass_detail'),
    path('<int:pk>/pdf/', views.gatepass_pdf_preview, name='gatepass_pdf_preview'),
    path('<int:pk>/send-email/', views.gatepass_send_email_view, name='gatepass_send_email'),
    path('seed-sample/', views.seed_sample_view, name='seed_sample'),
]
