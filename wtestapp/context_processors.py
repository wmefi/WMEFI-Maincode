from .models import Doctor, Agreement

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
            profile_complete = all([
                doctor.first_name,
                doctor.last_name,
                doctor.mobile,
                doctor.email,
                doctor.specialty
            ])
            
            # Check if agreement is signed
            agreement_signed = Agreement.objects.filter(doctor=doctor).exists() and doctor.agreement_accepted
            
            return {
                'doctor': doctor,
                'profile_complete': profile_complete,
                'agreement_signed': agreement_signed
            }
        except Doctor.DoesNotExist:
            return {
                'profile_complete': False,
                'agreement_signed': False
            }
    
    return {
        'profile_complete': False,
        'agreement_signed': False
    }