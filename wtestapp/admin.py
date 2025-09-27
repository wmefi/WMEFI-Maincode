from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Doctor, Survey, Question, Answer, Agreement, SurveyResponse, SurveyAssignment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'first_name', 'last_name', 'email', 'specialty', 'portal_type', 'agreement_amount', 'agreement_accepted', 'created_at')
    list_editable = ('agreement_amount', 'agreement_accepted')
    search_fields = ('user__username', 'mobile', 'first_name', 'last_name', 'email', 'specialty')
    list_filter = ('portal_type', 'specialty', 'gender', 'has_gst', 'agreement_accepted')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of extra forms to display
    fields = ('question_text', 'question_type', 'options')  # Explicitly define fields
    readonly_fields = ()  # No readonly fields initially
    can_delete = True  # Allow deleting questions
    show_change_link = True  # Add a link to the question's change form

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'portal_type', 'created_at', 'upload_survey_button')
    filter_horizontal = ('assigned_to',)
    search_fields = ('title', 'description')
    inlines = [QuestionInline]  # Add this line

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-survey/', self.admin_site.admin_view(self.upload_survey_view), name='upload_survey'),
        ]
        return custom_urls + urls

    def upload_survey_view(self, request):
        return redirect('upload_survey_file')
    
    def upload_survey_button(self, obj):
        from django.utils.html import format_html
        return format_html('<a class="button" href="{}">Upload New Survey</a>', 
                           '/survey/upload/') # Direct URL to the upload view

    upload_survey_button.short_description = "Upload"
    upload_survey_button.allow_tags = True

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'options')
    list_filter = ('survey', 'question_type')
    search_fields = ('question_text',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_doctor', 'get_survey', 'answer_text', 'created_at')
    list_filter = ('survey_response__doctor', 'question__survey', 'created_at')
    search_fields = ('survey_response__doctor__user__username', 'question__question_text', 'answer_text')

    def get_doctor(self, obj):
        return obj.survey_response.doctor
    get_doctor.short_description = 'Doctor'

    def get_survey(self, obj):
        return obj.question.survey
    get_survey.short_description = 'Survey'

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'signature_type', 'signed_at')
    search_fields = ('doctor__user__username', 'doctor__mobile')
    readonly_fields = ('signed_at',)

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'survey', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('is_completed', 'survey')
    search_fields = ('doctor__user__username', 'survey__title')


@admin.register(SurveyAssignment)
class SurveyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'survey', 'assigned_at')
    list_filter = ('survey__portal_type', 'doctor__portal_type')
    search_fields = ('doctor__user__username', 'doctor__mobile', 'survey__title')
