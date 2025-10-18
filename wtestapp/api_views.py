from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import Doctor, Survey, SurveyResponse, Agreement, Question
from django.utils import timezone
import pandas as pd
from io import BytesIO


@require_http_methods(["GET"])
def api_researchers_list(request):
    """API endpoint to get all researchers/doctors with their survey status.
    Optional filters via query params:
      - mode: CP | GC (filter by portal_type)
      - survey_id: int (show only doctors assigned to this survey)
    """
    
    mode = request.GET.get('mode', '').upper()
    survey_id = request.GET.get('survey_id')

    doctors_qs = Doctor.objects.all().select_related('custom_user')
    if mode in ('CP', 'GC'):
        doctors_qs = doctors_qs.filter(portal_type=mode)
    if survey_id:
        try:
            doctors_qs = doctors_qs.filter(surveys__id=int(survey_id)).distinct()
        except ValueError:
            pass

    doctors = doctors_qs
    
    researchers_data = []
    for doctor in doctors:
        # Get survey stats for this doctor
        total_surveys = Survey.objects.filter(assigned_to=doctor).count()
        completed_surveys = SurveyResponse.objects.filter(
            doctor=doctor, 
            is_completed=True
        ).count()
        in_progress_surveys = SurveyResponse.objects.filter(
            doctor=doctor, 
            is_completed=False
        ).count()
        
        # Calculate survey progress percentage
        if total_surveys > 0:
            survey_progress = int((completed_surveys / total_surveys) * 100)
        else:
            survey_progress = 0
        
        # Determine status
        if completed_surveys == total_surveys and total_surveys > 0:
            status = 'completed'
        elif in_progress_surveys > 0:
            status = 'in-progress'
        elif total_surveys > 0:
            status = 'pending'
        else:
            status = 'not-started'
        
        # Get completion date if completed
        completion_date = None
        if status == 'completed':
            last_response = SurveyResponse.objects.filter(
                doctor=doctor, 
                is_completed=True
            ).order_by('-completed_at').first()
            if last_response and last_response.completed_at:
                completion_date = last_response.completed_at.strftime('%Y-%m-%d')
        
        # Get last activity
        last_activity = 'Never'
        last_response = SurveyResponse.objects.filter(doctor=doctor).order_by('-started_at').first()
        if last_response and last_response.started_at:
            time_diff = timezone.now() - last_response.started_at
            if time_diff.days == 0:
                hours = time_diff.seconds // 3600
                if hours == 0:
                    minutes = time_diff.seconds // 60
                    last_activity = f'{minutes} minutes ago' if minutes > 0 else 'Just now'
                else:
                    last_activity = f'{hours} hours ago'
            elif time_diff.days == 1:
                last_activity = '1 day ago'
            else:
                last_activity = f'{time_diff.days} days ago'
        
        # Get name from custom_user or doctor fields
        if doctor.custom_user and doctor.custom_user.name:
            name = doctor.custom_user.name
        elif doctor.first_name or doctor.last_name:
            name = f"{doctor.first_name} {doctor.last_name}".strip()
        else:
            name = doctor.mobile or 'Unknown'
        
        # Determine ZSM/BDM from manager fields
        zsm_bdm = doctor.emp1_name or doctor.emp2_name or 'Not Assigned'
        
        researchers_data.append({
            'id': str(doctor.id),
            'name': name or 'Unknown',
            'mobile': doctor.mobile or (doctor.custom_user.mobile if doctor.custom_user else ''),
            'email': doctor.email or '',
            'unit': doctor.specialty or 'General',
            'specialty': doctor.specialty or 'General Medicine',
            'zsm': doctor.emp1_name or 'Not Assigned',
            'bdm': doctor.emp2_name or doctor.emp1_name or 'Not Assigned',
            'mode': doctor.portal_type if doctor.portal_type else 'CP',
            'status': status,
            'completionDate': completion_date,
            'location': doctor.territory or f"{doctor.city or ''}, {doctor.state or ''}".strip(', ') or 'Unknown',
            'experience': doctor.experience or 0,
            'rating': 4.5,  # Default rating
            'lastActivity': last_activity,
            'surveyProgress': survey_progress,
            'department': doctor.specialty or 'General Medicine',
            'joinDate': doctor.created_at.strftime('%Y-%m-%d') if doctor.created_at else '',
            'designation': doctor.designation or '',
            'emp1_mobile': doctor.emp1_mobile or '',
            'emp2_mobile': doctor.emp2_mobile or '',
        })
    
    return JsonResponse({
        'success': True,
        'researchers': researchers_data,
        'total': len(researchers_data)
    })


@require_http_methods(["GET"])
def api_dashboard_stats(request):
    """API endpoint to get dashboard statistics"""
    
    total_researchers = Doctor.objects.count()
    
    # Survey statistics
    completed_count = SurveyResponse.objects.filter(is_completed=True).values('doctor').distinct().count()
    
    # Get all doctors with assigned surveys
    doctors_with_surveys = Doctor.objects.filter(surveys__isnull=False).distinct()
    
    in_progress_count = 0
    pending_count = 0
    not_started_count = 0
    
    for doctor in doctors_with_surveys:
        total_assigned = Survey.objects.filter(assigned_to=doctor).count()
        completed = SurveyResponse.objects.filter(doctor=doctor, is_completed=True).count()
        in_progress = SurveyResponse.objects.filter(doctor=doctor, is_completed=False).count()
        
        if completed == total_assigned and total_assigned > 0:
            continue  # Already counted in completed_count
        elif in_progress > 0:
            in_progress_count += 1
        elif total_assigned > 0:
            pending_count += 1
        else:
            not_started_count += 1
    
    # Mode distribution
    cp_count = Doctor.objects.filter(portal_type='CP').count()
    gc_count = Doctor.objects.filter(portal_type='GC').count()
    
    # Completion rate
    if total_researchers > 0:
        completion_rate = int((completed_count / total_researchers) * 100)
    else:
        completion_rate = 0
    
    return JsonResponse({
        'success': True,
        'stats': {
            'totalResearchers': total_researchers,
            'completedSurveys': completed_count,
            'inProgressSurveys': in_progress_count,
            'pendingSurveys': pending_count,
            'notStartedSurveys': not_started_count,
            'cpResearchers': cp_count,
            'gcResearchers': gc_count,
            'completionRate': completion_rate,
        }
    })


@require_http_methods(["GET"])
def api_surveys_list(request):
    """Return list of surveys for populating filters in the React UI.
    Optional query param:
      - mode: CP | GC (filter by portal_type)
    """
    mode = request.GET.get('mode', '').upper()
    surveys_qs = Survey.objects.all().order_by('title')
    if mode in ('CP', 'GC'):
        surveys_qs = surveys_qs.filter(portal_type=mode)

    data = []
    for s in surveys_qs:
        data.append({
            'id': s.id,
            'title': s.title,
            'portal_type': s.portal_type or '',
            'assigned_count': s.assigned_to.count(),
        })
    return JsonResponse({'success': True, 'surveys': data})


@require_http_methods(["GET"])
def api_export_doctors_excel(request):
    """Export doctors + answers to Excel, similar to Django admin action.
    Query params:
      - mode: CP | GC | (empty for all)
      - survey_id: optional, export only this survey; else one sheet per survey assigned.
    """
    try:
        mode = request.GET.get('mode', '').upper()
        survey_id = request.GET.get('survey_id')

        doctors_qs = Doctor.objects.all().select_related('custom_user').prefetch_related('surveys')
        if mode in ('CP', 'GC'):
            doctors_qs = doctors_qs.filter(portal_type=mode)
        if survey_id:
            try:
                doctors_qs = doctors_qs.filter(surveys__id=int(survey_id)).distinct()
            except ValueError:
                pass

        # Determine surveys set
        if survey_id:
            surveys = list(Survey.objects.filter(id=survey_id))
        else:
            surveys = list(Survey.objects.filter(assigned_to__in=doctors_qs).distinct().order_by('title'))

        if not surveys:
            return JsonResponse({'success': False, 'message': 'No surveys found for the selected filters'}, status=400)

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')

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
            survey_doctors = doctors_qs.filter(surveys=survey)
            for doctor in survey_doctors:
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

                response_obj = SurveyResponse.objects.filter(doctor=doctor, survey=survey).first()
                row.update({
                    'Survey Completed': 'Yes' if (response_obj and response_obj.is_completed) else 'No',
                    'Survey Completed At': response_obj.completed_at.strftime('%Y-%m-%d %H:%M:%S') if (response_obj and response_obj.completed_at) else '',
                })

                answers_by_qid = {}
                if response_obj:
                    for ans in response_obj.answers.all().select_related('question'):
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
        http_response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = 'doctors_survey_export.xlsx' if len(surveys) != 1 else f"doctors_{surveys[0].title[:20]}_export.xlsx"
        http_response['Content-Disposition'] = f'attachment; filename={filename}'
        return http_response
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error exporting: {str(e)}'}, status=500)
