from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='home'),  # Root opens login directly
    path('login/', views.login, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor_profile/view/', views.doctor_profile_view, name='doctor_profile_view'),
    path('doctor_profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('doctor_profile/gc/', views.doctor_profile_gc, name='doctor_profile_gc'),
    path('doctor_profile_gc/', views.doctor_profile_gc),
    path('doctor_status/', views.doctor_status, name='doctor_status'),
    path('survey/upload/', views.upload_survey_file, name='upload_survey_file'),
    path('doctor/surveys/', views.doctor_surveys_list, name='doctor_surveys_list'),
    path('doctor/survey1/', views.survey1, name='survey1'),
    path('doctor/surveys/<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('doctor/surveys/done/', views.survey_done, name='survey_done'),
    path('logout/', views.logout_view, name='logout'),
    path('agreement/', views.agreement_page, name='agreement_page'),
    path('accept-agreement/', views.accept_agreement, name='accept_agreement'),
    path('download-agreement-pdf/', views.download_agreement_pdf, name='download_agreement_pdf'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin_dashboard/', views.admin_dashboard_view),
]
