from .models import Doctor

def doctor_context(request):
    mobile = request.session.get('mobile')
    if mobile:
        try:
            doctor = Doctor.objects.get(mobile=mobile)
            return {'doctor': doctor}
        except Doctor.DoesNotExist:
            return {}
    return {}