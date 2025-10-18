from .models import Doctor, Agreement, Survey, SurveyResponse

def doctor_context(request):
    mobile = request.session.get('mobile')
    doctor_id = request.session.get('doctor_id')
    
    if mobile or doctor_id:
        try:
            if doctor_id:
                doctor = Doctor.objects.get(id=doctor_id)
            else:
                doctor = Doctor.objects.get(mobile=mobile)
            
            # Check if profile is complete (basic fields filled)
            # last_name is optional now
            profile_complete = all([
                doctor.first_name,
                doctor.mobile,
                doctor.email,
                doctor.specialty or doctor.profession
            ])
            
            # Check if any agreement is signed (for navbar display)
            agreement_signed = Agreement.objects.filter(
                doctor=doctor,
                digital_signature__isnull=False,
                signed_at__isnull=False
            ).exists()
            
            # Get pending surveys and check unsigned surveys
            assigned_surveys = Survey.objects.filter(assigned_to=doctor)
            completed_survey_ids = SurveyResponse.objects.filter(doctor=doctor, is_completed=True).values_list('survey_id', flat=True)
            pending_surveys = assigned_surveys.exclude(id__in=completed_survey_ids)
            
            # Get signed survey IDs
            signed_survey_ids = Agreement.objects.filter(
                doctor=doctor,
                digital_signature__isnull=False,
                signed_at__isnull=False
            ).values_list('survey_id', flat=True)
            
            surveys_without_agreement = pending_surveys.exclude(id__in=signed_survey_ids)
            has_unsigned_surveys = surveys_without_agreement.exists()
            
            return {
                'doctor': doctor,
                'profile_complete': profile_complete,
                'agreement_signed': agreement_signed,
                'nav_pending_surveys': pending_surveys,
                'nav_surveys_without_agreement': surveys_without_agreement,
                'nav_has_unsigned_surveys': has_unsigned_surveys
            }
        except Doctor.DoesNotExist:
            return {
                'profile_complete': False,
                'agreement_signed': False,
                'nav_has_unsigned_surveys': False
            }
    
    return {
        'profile_complete': False,
        'agreement_signed': False,
        'nav_has_unsigned_surveys': False
    }