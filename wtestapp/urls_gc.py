from django.urls import path
from . import views

# GC portal URLs: exclude verify-otp so it is only available under CP/root
urlpatterns = [
    path('', views.login, name='gc_home'),
    path('login/', views.login, name='gc_login'),
    # path('verify-otp/', ...)  # intentionally omitted for GC
    path('doctor_profile/', views.doctor_profile, name='gc_doctor_profile'),
    path('doctor_profile/view/', views.doctor_profile_view, name='gc_doctor_profile_view'),
    path('doctor_profile/edit/', views.doctor_profile_edit, name='gc_doctor_profile_edit'),
    path('doctor_profile/gc/', views.doctor_profile_gc, name='gc_doctor_profile_gc'),
    path('doctor_profile_gc/', views.doctor_profile_gc),
    path('doctor_status/', views.doctor_status, name='gc_doctor_status'),
    path('survey/upload/', views.upload_survey_file, name='gc_upload_survey_file'),
    path('doctor/surveys/', views.doctor_surveys_list, name='gc_doctor_surveys_list'),
    path('doctor/survey1/', views.survey1, name='gc_survey1'),
    path('doctor/surveys/<int:survey_id>/', views.survey_detail, name='gc_survey_detail'),
    path('doctor/surveys/done/', views.survey_done, name='gc_survey_done'),
    path('logout/', views.logout_view, name='gc_logout'),
    path('agreement/', views.agreement_page, name='gc_agreement_page'),
    path('accept-agreement/', views.accept_agreement, name='gc_accept_agreement'),
    path('download-agreement-pdf/', views.download_agreement_pdf, name='gc_download_agreement_pdf'),
    path('admin-dashboard/', views.admin_dashboard_view, name='gc_admin_dashboard'),
    path('admin_dashboard/', views.admin_dashboard_view),
]
