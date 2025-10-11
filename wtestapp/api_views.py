from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import Doctor, Survey, SurveyResponse
from django.utils import timezone


@require_http_methods(["GET"])
def api_researchers_list(request):
    """API endpoint to get all researchers/doctors with their survey status"""
    
    doctors = Doctor.objects.all().select_related('custom_user')
    
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
