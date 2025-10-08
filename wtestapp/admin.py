import pandas as pd
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from .models import DoctorExcelUpload, Doctor, Survey, SurveyAssignment, Question, Agreement, SurveyResponse, Answer
import json
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

@admin.register(DoctorExcelUpload)
class DoctorExcelUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "excel_file", "survey_json", "uploaded_at", "reupload_link")
    actions = ["process_upload"]
    fields = ("excel_file", "survey_json", "uploaded_at")
    readonly_fields = ("uploaded_at",)
    
    def reupload_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:wtestapp_doctorexcelupload_change', args=[obj.id])
        return format_html('<a href="{}">Re-upload</a>', url)
    reupload_link.short_description = "Actions"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Process upload on both create and edit/re-upload
        files_changed = False
        if change:
            # Check if files were changed during edit
            if 'excel_file' in form.changed_data or 'survey_json' in form.changed_data:
                files_changed = True
                messages.info(request, "🔄 Files updated. Re-processing upload...")
        
        if not change or files_changed:
            self._process_single_upload(request, obj)

    def _process_single_upload(self, request, upload):
        try:
            df = pd.read_excel(upload.excel_file.path)
            logger.info(f"Auto-processing upload ID {upload.id}")
            logger.info(f"Excel columns: {df.columns.tolist()}")
            imported_doctors = []
            survey_json_data = None

            if upload.survey_json:
                try:
                    with upload.survey_json.open('r') as f:
                        survey_json_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Error reading JSON: {e}")
                    messages.warning(request, f"⚠️ Could not read survey JSON file: {e}")

            column_mapping = {col.strip().lower(): col for col in df.columns}
            
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                
                doctor_name = str(row_dict.get("Dr name as per PAN", "") or "").strip()
                doctor_email = str(row_dict.get("Dr email ID", "") or "").strip()
                
                if pd.isna(row_dict.get("Dr Contact number")):
                    doctor_mobile = ""
                else:
                    doctor_mobile = str(int(float(row_dict.get("Dr Contact number")))).strip()
                
                survey_col = None
                for col in df.columns:
                    if "survey" in col.lower() and "name" in col.lower():
                        survey_col = col
                        break
                
                survey_name = str(row_dict.get(survey_col, "") or "").strip() if survey_col else ""
                
                try:
                    survey_amount = float(row_dict.get("Amount", 0) or 0)
                except (ValueError, TypeError):
                    survey_amount = 0

                if not doctor_mobile:
                    continue

                doctor, created = Doctor.objects.get_or_create(
                    mobile=doctor_mobile,
                    defaults={
                        "first_name": doctor_name,
                        "email": doctor_email,
                        "contact_info": doctor_mobile,
                    },
                )
                
                doctor.first_name = doctor_name
                doctor.email = doctor_email
                doctor.contact_info = doctor_mobile
                doctor.last_name = ""
                doctor.save()
                
                imported_doctors.append(doctor)

                final_survey_name = survey_name if survey_name else "Auto Imported Survey"
                
                survey, survey_created = Survey.objects.get_or_create(
                    title=final_survey_name,
                    defaults={
                        "survey_json": upload.survey_json if upload.survey_json else None,
                        "amount": survey_amount,
                    },
                )
                
                if not survey_created:
                    survey.amount = survey_amount
                    if upload.survey_json:
                        survey.survey_json = upload.survey_json
                    survey.save()

                if survey_created and survey_json_data:
                    try:
                        questions = (
                            survey_json_data.get("questions")
                            or survey_json_data.get("items")
                            or survey_json_data.get("fields")
                            or survey_json_data.get("form")
                            or []
                        )
                        if isinstance(questions, list):
                            for idx, q in enumerate(questions):
                                if not isinstance(q, dict):
                                    continue

                                question_text = (
                                    q.get("question_text")
                                    or q.get("text")
                                    or q.get("question")
                                    or q.get("label")
                                    or q.get("title")
                                    or f"Question {idx+1}"
                                )

                                question_type = q.get("type", "radio")
                                options_list = q.get("options", [])
                                options_str = json.dumps(options_list) if options_list else ""

                                Question.objects.create(
                                    survey=survey,
                                    question_text=question_text,
                                    question_type=question_type,
                                    options=options_str,
                                    order=idx,
                                )
                    except Exception as e:
                        logger.error(f"Error creating questions: {e}")

                SurveyAssignment.objects.get_or_create(doctor=doctor, survey=survey)
                survey.assigned_to.add(doctor)

                Agreement.objects.update_or_create(
                    doctor=doctor,
                    defaults={
                        "survey": survey,
                        "amount": survey_amount,
                    }
                )

            messages.success(
                request,
                f"✅ Auto-imported {len(imported_doctors)} doctors with surveys and agreements!"
            )

        except Exception as e:
            logger.error(f"Error auto-processing upload: {e}", exc_info=True)
            messages.error(request, f"❌ Error while auto-processing file: {str(e)}")

    def process_upload(self, request, queryset):
        for upload in queryset:
            try:
                df = pd.read_excel(upload.excel_file.path)
                logger.info(f"Excel columns: {df.columns.tolist()}")
                imported_doctors = []
                survey_json_data = None

                if upload.survey_json:
                    try:
                        with upload.survey_json.open('r') as f:
                            survey_json_data = json.load(f)
                    except Exception as e:
                        logger.warning(f"Error reading JSON: {e}")
                        messages.warning(request, f"⚠️ Could not read survey JSON file: {e}")

                column_mapping = {col.strip().lower(): col for col in df.columns}
                logger.info(f"Available columns: {list(df.columns)}")
                
                for idx, row in df.iterrows():
                    row_dict = row.to_dict()
                    
                    doctor_name = str(row_dict.get("Dr name as per PAN", "") or "").strip()
                    doctor_email = str(row_dict.get("Dr email ID", "") or "").strip()
                    
                    if pd.isna(row_dict.get("Dr Contact number")):
                        doctor_mobile = ""
                    else:
                        doctor_mobile = str(int(float(row_dict.get("Dr Contact number")))).strip()
                    
                    survey_col = None
                    for col in df.columns:
                        if "survey" in col.lower() and "name" in col.lower():
                            survey_col = col
                            break
                    
                    survey_name = str(row_dict.get(survey_col, "") or "").strip() if survey_col else ""
                    
                    try:
                        survey_amount = float(row_dict.get("Amount", 0) or 0)
                    except (ValueError, TypeError):
                        survey_amount = 0

                    if not doctor_mobile:
                        continue
                    
                    logger.info(f"Processing: Name='{doctor_name}', Mobile='{doctor_mobile}', Email='{doctor_email}', Survey='{survey_name}', Amount={survey_amount}")

                    doctor, created = Doctor.objects.get_or_create(
                        mobile=doctor_mobile,
                        defaults={
                            "first_name": doctor_name,
                            "email": doctor_email,
                            "contact_info": doctor_mobile,
                        },
                    )
                    
                    doctor.first_name = doctor_name
                    doctor.email = doctor_email
                    doctor.contact_info = doctor_mobile
                    doctor.last_name = ""
                    doctor.save()
                    
                    logger.info(f"Saved Doctor: ID={doctor.id}, Name='{doctor.first_name}', Mobile='{doctor.mobile}'")
                    imported_doctors.append(doctor)

                    final_survey_name = survey_name if survey_name else "Auto Imported Survey"
                    
                    survey, survey_created = Survey.objects.get_or_create(
                        title=final_survey_name,
                        defaults={
                            "survey_json": upload.survey_json if upload.survey_json else None,
                            "amount": survey_amount,
                        },
                    )
                    
                    if not survey_created:
                        survey.amount = survey_amount
                        if upload.survey_json:
                            survey.survey_json = upload.survey_json
                        survey.save()
                    
                    logger.info(f"Survey: ID={survey.id}, Title='{survey.title}', Amount={survey.amount}")

                    if survey_created and survey_json_data:
                        try:
                            questions = (
                                survey_json_data.get("questions")
                                or survey_json_data.get("items")
                                or survey_json_data.get("fields")
                                or survey_json_data.get("form")
                                or []
                            )
                            if isinstance(questions, list):
                                for idx, q in enumerate(questions):
                                    if not isinstance(q, dict):
                                        continue

                                    question_text = (
                                        q.get("question_text")
                                        or q.get("text")
                                        or q.get("question")
                                        or q.get("label")
                                        or q.get("title")
                                        or f"Question {idx+1}"
                                    )

                                    question_type = q.get("type", "radio")
                                    options_list = q.get("options", [])
                                    options_str = json.dumps(options_list) if options_list else ""

                                    Question.objects.create(
                                        survey=survey,
                                        question_text=question_text,
                                        question_type=question_type,
                                        options=options_str,
                                        order=idx,
                                    )
                        except Exception as e:
                            logger.error(f"Error creating questions: {e}")

                    assignment, assign_created = SurveyAssignment.objects.get_or_create(doctor=doctor, survey=survey)
                    survey.assigned_to.add(doctor)
                    logger.info(f"Assignment: Doctor {doctor.mobile} -> Survey '{survey.title}' (Created: {assign_created})")

                    agreement, agr_created = Agreement.objects.update_or_create(
                        doctor=doctor,
                        defaults={
                            "survey": survey,
                            "amount": survey_amount,
                        }
                    )
                    logger.info(f"Agreement: Doctor {doctor.mobile}, Survey '{survey.title}', Amount={agreement.amount} (Created: {agr_created})")

                messages.success(
                    request,
                    f"✅ Imported {len(imported_doctors)} doctors with surveys and agreements!"
                )

            except Exception as e:
                logger.error(f"Error processing upload: {e}", exc_info=True)
                messages.error(request, f"❌ Error while processing file: {str(e)}")

    process_upload.short_description = "Process Excel + Auto-Link Survey JSON"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "get_doctor_name", "mobile", "email", "get_assigned_surveys", "created_at")
    search_fields = ("first_name", "last_name", "mobile", "email")
    list_filter = ("portal_type", "created_at")
    readonly_fields = ("created_at", "updated_at")

    def get_doctor_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.mobile
    get_doctor_name.short_description = "Doctor Name"

    def get_assigned_surveys(self, obj):
        surveys = obj.surveys.all()[:3]
        return ", ".join([s.title for s in surveys]) if surveys else "No surveys"
    get_assigned_surveys.short_description = "Assigned Surveys"


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "amount", "get_assigned_count", "created_at")
    search_fields = ("title",)
    list_filter = ("portal_type", "created_at")

    def get_assigned_count(self, obj):
        return obj.assigned_to.count()
    get_assigned_count.short_description = "Assigned Doctors"


@admin.register(SurveyAssignment)
class SurveyAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "get_doctor_name", "get_survey_title", "assigned_at")
    search_fields = ("doctor__first_name", "doctor__mobile", "survey__title")
    list_filter = ("assigned_at",)

    def get_doctor_name(self, obj):
        return str(obj.doctor)
    get_doctor_name.short_description = "Doctor"

    def get_survey_title(self, obj):
        return obj.survey.title
    get_survey_title.short_description = "Survey"


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "get_doctor_name", "get_survey_title", "amount", "signed_at")
    search_fields = ("doctor__first_name", "doctor__mobile")
    list_filter = ("signed_at",)

    def get_doctor_name(self, obj):
        return str(obj.doctor)
    get_doctor_name.short_description = "Doctor"

    def get_survey_title(self, obj):
        return obj.survey.title if obj.survey else "N/A"
    get_survey_title.short_description = "Survey"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "survey", "question_text", "question_type", "order")
    list_filter = ("survey", "question_type")
    search_fields = ("question_text",)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('question', 'answer_text', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_doctor_name', 'get_doctor_mobile', 'survey', 'is_completed', 'completed_at', 'view_answers_link')
    list_filter = ('survey', 'is_completed', 'completed_at')
    search_fields = ('doctor__first_name', 'doctor__mobile', 'survey__title')
    readonly_fields = ('started_at', 'completed_at')
    inlines = [AnswerInline]
    actions = ['export_to_excel']
    
    def get_doctor_name(self, obj):
        if obj.doctor:
            # Show actual name, fallback to mobile if name not available
            full_name = f"{obj.doctor.first_name} {obj.doctor.last_name}".strip()
            return full_name if full_name else obj.doctor.mobile
        return 'N/A'
    get_doctor_name.short_description = 'Doctor Name'
    
    def get_doctor_mobile(self, obj):
        return obj.doctor.mobile if obj.doctor else 'N/A'
    get_doctor_mobile.short_description = 'Contact Number'
    
    def view_answers_link(self, obj):
        count = obj.answers.count()
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{} answers</span>',
            count
        )
    view_answers_link.short_description = 'Answers'
    
    def export_to_excel(self, request, queryset):
        """Export selected survey responses to Excel"""
        try:
            # Create Excel writer
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            
            # Prepare data for each response
            all_data = []
            
            for response in queryset:
                # Get actual doctor name
                doctor_name = 'N/A'
                if response.doctor:
                    full_name = f"{response.doctor.first_name} {response.doctor.last_name}".strip()
                    doctor_name = full_name if full_name else response.doctor.mobile
                
                row_data = {
                    'Response ID': response.id,
                    'Doctor Name': doctor_name,
                    'Contact Number': response.doctor.mobile if response.doctor else 'N/A',
                    'Email': response.doctor.email or 'N/A',
                    'Survey': response.survey.title,
                    'Completed': 'Yes' if response.is_completed else 'No',
                    'Submitted At': response.completed_at.strftime('%Y-%m-%d %H:%M:%S') if response.completed_at else 'Not completed',
                }
                
                # Add all answers as columns
                for answer in response.answers.all():
                    question_text = answer.question.question_text
                    # Truncate question if too long for column name
                    if len(question_text) > 50:
                        question_text = question_text[:47] + '...'
                    row_data[question_text] = answer.answer_text or ''
                
                all_data.append(row_data)
            
            # Create DataFrame
            df = pd.DataFrame(all_data)
            
            # Write to Excel
            df.to_excel(writer, sheet_name='Survey Responses', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Survey Responses']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                # Handle column letters properly for more than 26 columns
                if idx < 26:
                    col_letter = chr(65 + idx)
                else:
                    col_letter = chr(65 + (idx // 26) - 1) + chr(65 + (idx % 26))
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)
            
            writer.close()
            output.seek(0)
            
            # Create HTTP response
            http_response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            http_response['Content-Disposition'] = 'attachment; filename=survey_responses.xlsx'
            
            self.message_user(request, f'✅ Successfully exported {queryset.count()} survey responses to Excel', messages.SUCCESS)
            return http_response
            
        except Exception as e:
            self.message_user(request, f'❌ Error exporting to Excel: {str(e)}', messages.ERROR)
            return
    
    export_to_excel.short_description = '📊 Export Selected to Excel'


# Answer admin removed - not needed for users
