from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Doctor, Survey, Question, Answer, Agreement, SurveyResponse, SurveyAssignment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'mobile', 'first_name', 'last_name', 'email', 'specialty', 'portal_type', 'agreement_amount', 'agreement_accepted', 'created_at')
    list_editable = ('agreement_amount', 'agreement_accepted')
    search_fields = ('mobile', 'first_name', 'last_name', 'email', 'specialty')
    list_filter = ('portal_type', 'specialty', 'gender', 'has_gst', 'agreement_accepted')
    
    def get_doctor_name(self, obj):
        if obj.user and hasattr(obj.user, 'username') and obj.user.username:
            return obj.user.username
        elif obj.first_name or obj.last_name:
            return f"Dr. {obj.first_name} {obj.last_name}".strip()
        elif obj.mobile:
            return obj.mobile
        return f"Doctor #{obj.id}"
    get_doctor_name.short_description = 'Doctor'

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'portal_type', 'amount', 'created_at', 'get_questions_count')
    list_editable = ('amount',)
    filter_horizontal = ('assigned_to',)
    search_fields = ('title',)
    fields = ('title', 'survey_json', 'portal_type', 'amount', 'assigned_to')
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "assigned_to":
            kwargs["queryset"] = db_field.related_model.objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_questions_count(self, obj):
        from .models import Question
        count = Question.objects.filter(survey=obj).count()
        return f"{count} questions"
    get_questions_count.short_description = 'Questions'
    
    def save_model(self, request, obj, form, change):
        import json
        from .models import Question
        import logging
        logger = logging.getLogger(__name__)
        
        # Save the survey first
        super().save_model(request, obj, form, change)
        
        # If JSON file is uploaded, create questions from it
        if obj.survey_json and not change:  # Only on creation
            try:
                with obj.survey_json.open('r') as f:
                    json_data = json.load(f)
                
                # Extract questions from JSON
                questions = []
                if isinstance(json_data, dict):
                    questions = (
                        json_data.get('questions')
                        or json_data.get('items')
                        or json_data.get('fields')
                        or json_data.get('form')
                        or []
                    )
                elif isinstance(json_data, list):
                    questions = json_data
                
                # Create Question objects
                for idx, q in enumerate(questions):
                    if not isinstance(q, dict):
                        continue
                    
                    question_text = (
                        q.get('question_text')
                        or q.get('text')
                        or q.get('question')
                        or q.get('label')
                        or q.get('title')
                        or f'Question {idx+1}'
                    )
                    
                    question_type = q.get('type', 'radio')
                    if 'options' in q:
                        question_type = 'radio'
                    elif question_type not in ['text', 'textarea', 'radio', 'checkbox', 'select', 'file']:
                        question_type = 'radio'
                    
                    options_list = q.get('options', [])
                    options_str = json.dumps(options_list) if options_list else ''
                    
                    Question.objects.create(
                        survey=obj,
                        question_text=question_text,
                        question_type=question_type,
                        options=options_str,
                        order=idx
                    )
                
                from django.contrib import messages
                messages.success(request, f'Survey created with {len(questions)} questions from JSON file!')
                logger.info(f"Created {len(questions)} questions for survey: {obj.title}")
                
            except Exception as e:
                logger.error(f"Error loading questions from JSON: {str(e)}")
                from django.contrib import messages
                messages.warning(request, f'Survey created but error loading questions from JSON: {str(e)}')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'options')
    list_filter = ('survey', 'question_type')
    search_fields = ('question_text',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'get_doctor', 'get_survey', 'answer_text', 'created_at')
    list_filter = ('question__survey', 'created_at')
    search_fields = ('survey_response__doctor__mobile', 'survey_response__doctor__first_name', 'survey_response__doctor__last_name', 'question__question_text', 'answer_text')

    def get_doctor(self, obj):
        if obj.survey_response and obj.survey_response.doctor:
            return str(obj.survey_response.doctor)
        return "No Doctor"
    get_doctor.short_description = 'Doctor'

    def get_survey(self, obj):
        return obj.question.survey
    get_survey.short_description = 'Survey'

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_display', 'survey', 'amount', 'signature_type', 'signed_at')
    list_filter = ('signature_type', 'signed_at')
    search_fields = ('doctor__mobile', 'doctor__first_name', 'doctor__last_name', 'survey__title')
    readonly_fields = ('signed_at',)
    
    def get_doctor_display(self, obj):
        if obj.doctor:
            return str(obj.doctor)
        return "No Doctor"
    get_doctor_display.short_description = 'Doctor'
    fieldsets = (
        (None, {
            'fields': ('doctor', 'survey', 'amount')
        }),
        ('Agreement Details (Optional)', {
            'classes': ('collapse',),
            'fields': ('agreement_text',),
        }),
        ('Signature', {
            'fields': ('digital_signature', 'signature_type', 'signed_at'),
        }),
        ('Additional Info', {
            'classes': ('collapse',),
            'fields': ('pdf_file', 'ip_address', 'user_agent'),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:  # Only show required fields in add form
            fieldsets = (
                (None, {
                    'fields': ('doctor', 'survey', 'amount')
                }),
                ('Agreement Text (Optional)', {
                    'fields': ('agreement_text',),
                }),
            )
        return fieldsets

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_display', 'survey', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('is_completed', 'survey')
    search_fields = ('doctor__mobile', 'doctor__first_name', 'doctor__last_name', 'survey__title')
    
    def get_doctor_display(self, obj):
        if obj.doctor:
            return str(obj.doctor)
        return "No Doctor"
    get_doctor_display.short_description = 'Doctor'


@admin.register(SurveyAssignment)
class SurveyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_display', 'survey', 'assigned_at')
    list_filter = ('survey__portal_type', 'doctor__portal_type')
    search_fields = ('doctor__mobile', 'doctor__first_name', 'doctor__last_name', 'survey__title')
    
    def get_doctor_display(self, obj):
        if obj.doctor:
            return str(obj.doctor)
        return "No Doctor"
    get_doctor_display.short_description = 'Doctor'
