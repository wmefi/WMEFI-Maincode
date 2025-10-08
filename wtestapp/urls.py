from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor_profile/view/', views.doctor_profile_view, name='doctor_profile_view'),
    path('doctor_profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('surveys/', views.doctor_surveys_list, name='surveys'),
    path('doctor/surveys/<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('doctor/surveys/done/<int:response_id>/', views.survey_done, name='survey_done'),
    path('agreement/<int:survey_id>/', views.agreement_page, name='agreement_page'),
    path('download-agreement/', views.download_agreement, name='download_agreement'),
    path('request-agreement-otp/', views.request_agreement_otp, name='request_agreement_otp'),
    path('verify-agreement-otp/', views.verify_agreement_otp, name='verify_agreement_otp'),
    path('download-survey/<int:response_id>/', views.download_survey_pdf, name='download_survey_pdf'),
    path('sign-agreement/', views.sign_agreement, name='sign_agreement'),
    path('api/get-doctor-survey/', views.get_doctor_survey_api, name='get_doctor_survey_api'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
