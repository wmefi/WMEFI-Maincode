import pandas as pd
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html
from .models import DoctorExcelUpload, Doctor, Survey, SurveyAssignment, Question, Agreement, SurveyResponse, Answer
import json
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class SurveyAssignmentFilter(admin.SimpleListFilter):
    title = 'Survey'
    parameter_name = 'survey'

    def lookups(self, request, model_admin):
        from .models import Survey
        return [(str(s.id), s.title) for s in Survey.objects.all().order_by('title')]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(surveys__id=value).distinct()
        return queryset

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
                specialty = str(row_dict.get("speciality", "") or "").strip()
                
                if pd.isna(row_dict.get("Dr Contact number")):
                    doctor_mobile = ""
                else:
                    doctor_mobile = str(int(float(row_dict.get("Dr Contact number")))).strip()
                
                # Extract manager and territory details
                territory = str(row_dict.get("Territory To Which Doctor Is Associated", "") or row_dict.get("Territory", "") or "").strip()
                emp1_name = str(row_dict.get("Emp1 Name", "") or "").strip()
                emp1_mobile_raw = row_dict.get("Emp1 Mobile", "")
                emp1_mobile = str(int(float(emp1_mobile_raw))).strip() if not pd.isna(emp1_mobile_raw) else ""
                
                emp2_name = str(row_dict.get("Emp2 Name", "") or "").strip()
                emp2_mobile_raw = row_dict.get("emp2 Mobile", "")
                emp2_mobile = str(int(float(emp2_mobile_raw))).strip() if not pd.isna(emp2_mobile_raw) else ""
                
                designation = str(row_dict.get("Desig", "") or "").strip()
                
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
                        "specialty": specialty,
                        "territory": territory,
                        "emp1_name": emp1_name,
                        "emp1_mobile": emp1_mobile,
                        "emp2_name": emp2_name,
                        "emp2_mobile": emp2_mobile,
                        "designation": designation,
                    },
                )
                
                # Update existing doctor with all fields
                doctor.first_name = doctor_name
                doctor.email = doctor_email
                doctor.contact_info = doctor_mobile
                doctor.specialty = specialty
                doctor.territory = territory
                doctor.emp1_name = emp1_name
                doctor.emp1_mobile = emp1_mobile
                doctor.emp2_name = emp2_name
                doctor.emp2_mobile = emp2_mobile
                doctor.designation = designation
                doctor.last_name = ""
                doctor.save()
                
                imported_doctors.append(doctor)

                # Create unique survey name with timestamp to avoid overwriting old surveys
                from django.utils import timezone
                import datetime
                
                if survey_name:
                    # Check if survey with this name already exists
                    existing_survey_count = Survey.objects.filter(title__startswith=survey_name).count()
                    if existing_survey_count > 0:
                        # Add number suffix to make it unique
                        final_survey_name = f"{survey_name} ({existing_survey_count + 1})"
                    else:
                        final_survey_name = survey_name
                else:
                    # If no survey name in Excel, use Auto Imported with timestamp
                    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
                    final_survey_name = f"Auto Imported Survey {timestamp}"
                
                # Always create NEW survey (no get_or_create to avoid updating old ones)
                survey = Survey.objects.create(
                    title=final_survey_name,
                    survey_json=upload.survey_json if upload.survey_json else None,
                    amount=survey_amount,
                )
                survey_created = True

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
                                options_data = q.get("options", None)
                                # Ensure JSONField gets proper JSON (list/dict). If a JSON string is provided, parse it.
                                if isinstance(options_data, str):
                                    try:
                                        options_data = json.loads(options_data)
                                    except Exception:
                                        # leave as-is if parsing fails
                                        pass

                                Question.objects.create(
                                    survey=survey,
                                    question_text=question_text,
                                    question_type=question_type,
                                    options=options_data if options_data else None,
                                    order=idx,
                                )
                    except Exception as e:
                        logger.error(f"Error creating questions: {e}")

                SurveyAssignment.objects.get_or_create(doctor=doctor, survey=survey)
                survey.assigned_to.add(doctor)

                # Create agreement for this survey if not exists
                Agreement.objects.get_or_create(
                    doctor=doctor,
                    survey=survey,
                    defaults={
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
                    specialty = str(row_dict.get("speciality", "") or "").strip()
                    
                    if pd.isna(row_dict.get("Dr Contact number")):
                        doctor_mobile = ""
                    else:
                        doctor_mobile = str(int(float(row_dict.get("Dr Contact number")))).strip()
                    
                    # Extract manager and territory details
                    territory = str(row_dict.get("Territory To Which Doctor Is Associated", "") or row_dict.get("Territory", "") or "").strip()
                    emp1_name = str(row_dict.get("Emp1 Name", "") or "").strip()
                    emp1_mobile_raw = row_dict.get("Emp1 Mobile", "")
                    emp1_mobile = str(int(float(emp1_mobile_raw))).strip() if not pd.isna(emp1_mobile_raw) else ""
                    
                    emp2_name = str(row_dict.get("Emp2 Name", "") or "").strip()
                    emp2_mobile_raw = row_dict.get("emp2 Mobile", "")
                    emp2_mobile = str(int(float(emp2_mobile_raw))).strip() if not pd.isna(emp2_mobile_raw) else ""
                    
                    designation = str(row_dict.get("Desig", "") or "").strip()
                    
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

                    # Debug: Print all column names and values
                    logger.info("\n=== Excel Column Names and Values ===")
                    for col_name, value in row_dict.items():
                        logger.info(f"Column: '{col_name}' = '{value}'")
                    
                    # Method 1: Check for common column names
                    portal_type = None
                    possible_columns = [
                        'Portal Type', 'portal_type', 'Mode', 'mode', 
                        'Type', 'type', 'Portal', 'portal'
                    ]
                    
                    # Look for exact matches first
                    for col in possible_columns:
                        if col in row_dict:
                            portal_type = str(row_dict[col] or '').strip().upper()
                            if portal_type in ['GC', 'CP']:
                                logger.info(f"Found portal type in column '{col}': {portal_type}")
                                break
                            portal_type = None
                    
                    # Method 2: Check all columns for GC/CP values
                    if not portal_type:
                        for col_name, value in row_dict.items():
                            if str(value).strip().upper() in ['GC', 'CP']:
                                portal_type = str(value).strip().upper()
                                logger.info(f"Found portal type value '{portal_type}' in column: {col_name}")
                                break
                    
                    # If still not found, use default
                    if not portal_type or portal_type not in ['GC', 'CP']:
                        portal_type = 'GC'
                        logger.warning(f"Using default portal type: {portal_type}")
                    else:
                        logger.info(f"Using portal type: {portal_type}")
                    
                    # Prepare doctor data with explicit fields
                    doctor_data = {
                        "first_name": doctor_name or "",
                        "email": doctor_email or "",
                        "contact_info": doctor_mobile or "",
                        "specialty": specialty or "",
                        "territory": territory or "",
                        "emp1_name": emp1_name or "",
                        "emp1_mobile": emp1_mobile or "",
                        "emp2_name": emp2_name or "",
                        "emp2_mobile": emp2_mobile or "",
                        "designation": designation or "",
                        "portal_type": portal_type,
                        "last_name": ""
                    }
                    
                    logger.info(f"Creating/updating doctor with data: {doctor_data}")
                    
                    # Create or update doctor
                    doctor, created = Doctor.objects.update_or_create(
                        mobile=doctor_mobile,
                        defaults=doctor_data
                    )
                    
                    logger.info(f"Saved Doctor: ID={doctor.id}, Name='{doctor.first_name}', Mobile='{doctor.mobile}', Territory='{territory}', Manager='{emp1_name}'")
                    imported_doctors.append(doctor)

                    # Create unique survey name with timestamp to avoid overwriting old surveys
                    from django.utils import timezone
                    import datetime
                    
                    if survey_name:
                        # Check if survey with this name already exists
                        existing_survey_count = Survey.objects.filter(title__startswith=survey_name).count()
                        if existing_survey_count > 0:
                            # Add number suffix to make it unique
                            final_survey_name = f"{survey_name} ({existing_survey_count + 1})"
                        else:
                            final_survey_name = survey_name
                    else:
                        # If no survey name in Excel, use Auto Imported with timestamp
                        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
                        final_survey_name = f"Auto Imported Survey {timestamp}"
                    
                    # Always create NEW survey (no get_or_create to avoid updating old ones)
                    survey = Survey.objects.create(
                        title=final_survey_name,
                        survey_json=upload.survey_json if upload.survey_json else None,
                        amount=survey_amount,
                    )
                    survey_created = True
                    
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
                                    options_data = q.get("options", None)
                                    # Ensure JSONField gets proper JSON (list/dict). If a JSON string is provided, parse it.
                                    if isinstance(options_data, str):
                                        try:
                                            options_data = json.loads(options_data)
                                        except Exception:
                                            # leave as-is if parsing fails
                                            pass

                                    Question.objects.create(
                                        survey=survey,
                                        question_text=question_text,
                                        question_type=question_type,
                                        options=options_data if options_data else None,
                                        order=idx,
                                    )
                        except Exception as e:
                            logger.error(f"Error creating questions: {e}")

                    assignment, assign_created = SurveyAssignment.objects.get_or_create(doctor=doctor, survey=survey)
                    survey.assigned_to.add(doctor)
                    logger.info(f"Assignment: Doctor {doctor.mobile} -> Survey '{survey.title}' (Created: {assign_created})")

                    # Create agreement for this survey if not exists
                    agreement, agr_created = Agreement.objects.get_or_create(
                        doctor=doctor,
                        survey=survey,
                        defaults={
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
    list_display = ("id", "get_doctor_name", "mobile", "email", "specialty", "territory", 
                   "emp1_name", "emp1_mobile", "created_at")
    search_fields = ("first_name", "last_name", "mobile", "email", "specialty", "territory",
                    "emp1_name", "emp1_mobile", "emp2_name", "emp2_mobile")
    list_filter = ("portal_type", "specialty", "territory", "created_at")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = True
    actions = ['export_doctors_with_answers_excel']

    def get_doctor_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.last_name else obj.first_name
    get_doctor_name.short_description = "Doctor Name"
    get_doctor_name.admin_order_field = 'first_name'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('surveys')

    def get_assigned_surveys(self, obj):
        return ", ".join([s.title for s in obj.surveys.all()])
    get_assigned_surveys.short_description = "Assigned Surveys"

    def export_doctors_with_answers_excel(self, request, queryset):
        try:
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')

            # Selected survey from sidebar filter (if any)
            selected_survey_id = request.GET.get('survey')
            from .models import Survey, SurveyResponse, Agreement, Question

            if selected_survey_id:
                surveys = list(Survey.objects.filter(id=selected_survey_id))
            else:
                surveys = list(Survey.objects.filter(assigned_to__in=queryset).distinct().order_by('title'))

            if not surveys:
                self.message_user(request, 'No surveys found for the selected doctors.', messages.WARNING)
                return

            doctors = queryset.select_related('custom_user').prefetch_related('surveys')

            for survey in surveys:
                rows = []
                questions = list(Question.objects.filter(survey=survey).order_by('order', 'id'))
                question_headers = []
                for q in questions:
                    header = q.question_text
                    if len(header) > 70:
                        header = header[:67] + '...'
                    question_headers.append((q.id, header))

                # Only doctors assigned to this survey
                for doctor in doctors.filter(surveys=survey):
                    full_name = f"{doctor.first_name} {doctor.last_name}".strip()
                    name = full_name if full_name else (doctor.custom_user.name if doctor.custom_user else doctor.mobile or '')

                    row = {
                        'Doctor ID': doctor.id,
                        'Doctor Name': name,
                        'Mobile': doctor.mobile or (doctor.custom_user.mobile if doctor.custom_user else ''),
                        'Email': doctor.email or '',
                        'Portal': doctor.portal_type or '',
                        'Territory': doctor.territory or '',
                        'Designation': doctor.designation or '',
                        'Manager 1 Name': doctor.emp1_name or '',
                        'Manager 1 Mobile': doctor.emp1_mobile or '',
                        'Manager 2 Name': doctor.emp2_name or '',
                        'Manager 2 Mobile': doctor.emp2_mobile or '',
                        'State': doctor.state or '',
                        'City': doctor.city or '',
                        'Specialty': doctor.specialty or '',
                        'Created At': doctor.created_at.strftime('%Y-%m-%d %H:%M:%S') if doctor.created_at else '',
                        'Survey Title': survey.title,
                        'Survey Amount': float(survey.amount or 0),
                    }

                    agreement = Agreement.objects.filter(doctor=doctor).first()
                    row.update({
                        'Agreement Signed': 'Yes' if (agreement and agreement.digital_signature and agreement.signed_at) else 'No',
                        'Agreement Signed At': agreement.signed_at.strftime('%Y-%m-%d %H:%M:%S') if (agreement and agreement.signed_at) else '',
                        'Agreement IP': agreement.ip_address if agreement else '',
                    })

                    response = SurveyResponse.objects.filter(doctor=doctor, survey=survey).first()
                    row.update({
                        'Survey Completed': 'Yes' if (response and response.is_completed) else 'No',
                        'Survey Completed At': response.completed_at.strftime('%Y-%m-%d %H:%M:%S') if (response and response.completed_at) else '',
                    })

                    answers_by_qid = {}
                    if response:
                        for ans in response.answers.all().select_related('question'):
                            answers_by_qid[ans.question_id] = ans.answer_text or ''

                    for qid, header in question_headers:
                        row[header] = answers_by_qid.get(qid, '')

                    rows.append(row)

                # Create DataFrame for this survey sheet
                if rows:
                    df = pd.DataFrame(rows)
                else:
                    df = pd.DataFrame(columns=['Doctor ID', 'Doctor Name'])

                sheet_name = survey.title[:31] if survey.title else f"Survey_{survey.id}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                ws = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns):
                    try:
                        max_len = max((df[col].astype(str).map(len).max() if not df.empty else 10), len(str(col)))
                    except Exception:
                        max_len = len(str(col))
                    col_letter = chr(65 + idx) if idx < 26 else chr(65 + (idx // 26) - 1) + chr(65 + (idx % 26))
                    ws.column_dimensions[col_letter].width = min(max_len + 2, 50)

            writer.close()
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = 'doctors_survey_export.xlsx' if len(surveys) != 1 else f"doctors_{surveys[0].title[:20]}_export.xlsx"
            response['Content-Disposition'] = f'attachment; filename={filename}'
            self.message_user(request, f'✅ Exported {queryset.count()} doctors across {len(surveys)} survey sheet(s).', messages.SUCCESS)
            return response
        except Exception as e:
            self.message_user(request, f'❌ Error exporting: {str(e)}', messages.ERROR)
            return

    export_doctors_with_answers_excel.short_description = '📥 Export filtered doctors + answers to Excel'


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


