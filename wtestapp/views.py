from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Doctor, CustomUser, Survey, Agreement, Question, SurveyResponse, Answer, SurveyAssignment
from .utils import send_sms
from .forms import DoctorForm
import logging
import json
from django.forms.models import model_to_dict
from django.utils import timezone
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def doctor_surveys_list(request):
    """View to display all surveys assigned to a doctor"""
    if 'mobile' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    try:
        doctor = None
        doctor_id = request.session.get('doctor_id')
        if doctor_id:
            doctor = Doctor.objects.get(id=doctor_id)
            
            pending_tasks = request.session.get('pending_tasks', [])
            if pending_tasks:
                for task in pending_tasks:
                    messages.info(request, task)
                del request.session['pending_tasks']
        else:
            mobile = request.session.get('mobile')
            if mobile:
                try:
                    doctor = Doctor.objects.get(mobile=mobile)
                except Doctor.DoesNotExist:
                    custom_user = CustomUser.objects.get(mobile=mobile)
                    doctor = Doctor.objects.get(custom_user=custom_user)
        if not doctor:
            raise Doctor.DoesNotExist("Doctor not found in session context")
        
        # Get all surveys assigned to this doctor
        assigned_surveys = Survey.objects.filter(assigned_to=doctor)
        
        # Get survey responses to track completion status
        completed_surveys = SurveyResponse.objects.filter(doctor=doctor, is_completed=True).values_list('survey_id', flat=True)
        
        context = {
            'doctor': doctor,
            'surveys': assigned_surveys,
            'completed_surveys': list(completed_surveys)
        }
        
        return render(request, 'wtestapp/doctor_surveys.html', context)
    except (CustomUser.DoesNotExist, Doctor.DoesNotExist):
        messages.error(request, "User or doctor profile not found")
        return redirect('login')

def survey_detail(request, survey_id):
    """View to display and handle survey questions and responses"""
    if 'mobile' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    try:
        doctor = None
        doctor_id = request.session.get('doctor_id')
        if doctor_id:
            doctor = Doctor.objects.get(id=doctor_id)
        else:
            mobile = request.session.get('mobile')
            if mobile:
                try:
                    doctor = Doctor.objects.get(mobile=mobile)
                except Doctor.DoesNotExist:
                    custom_user = CustomUser.objects.get(mobile=mobile)
                    doctor = Doctor.objects.get(custom_user=custom_user)
        if not doctor:
            raise Doctor.DoesNotExist("Doctor not found in session context")
        survey = get_object_or_404(Survey, id=survey_id)
        
        # Check if survey is assigned to this doctor
        if doctor not in survey.assigned_to.all():
            messages.error(request, "This survey is not assigned to you")
            return redirect('surveys')
        
        # If user is explicitly viewing, don't redirect even if completed
        view_mode = request.GET.get('view') == '1'
        existing_response = SurveyResponse.objects.filter(doctor=doctor, survey=survey, is_completed=True).first()
        if existing_response and not view_mode:
            messages.info(request, "You have already completed this survey")
            return redirect('survey_done', response_id=existing_response.id)
        
        # Get or create survey response
        survey_response, created = SurveyResponse.objects.get_or_create(
            doctor=doctor,
            survey=survey,
            defaults={'is_completed': False}
        )
        
        # Read JSON file for questions
        survey_json_data = None
        questions_from_json = []
        existing_answers_json = {}
        if survey.survey_json:
            try:
                import json
                with survey.survey_json.open('r') as f:
                    survey_json_data = json.load(f)
                    # Extract and normalize questions from JSON
                    raw_questions = []
                    if isinstance(survey_json_data, dict):
                        # Prefer 'questions', but auto-detect common alternatives
                        raw_questions = (
                            survey_json_data.get('questions')
                            or survey_json_data.get('items')
                            or survey_json_data.get('fields')
                            or survey_json_data.get('form')
                            or []
                        )
                    elif isinstance(survey_json_data, list):
                        raw_questions = survey_json_data

                    normalized_questions = []
                    for q in raw_questions:
                        if not isinstance(q, dict):
                            continue
                        text = (
                            q.get('text')
                            or q.get('question')
                            or q.get('question_text')
                            or q.get('label')
                            or q.get('title')
                            or ''
                        )
                        qtype = (
                            q.get('type')
                            or q.get('question_type')
                            or ('radio' if (q.get('options') or q.get('choices') or q.get('options_list')) else 'text')
                        )
                        # Map common aliases to our template-supported types
                        type_map = {
                            'single': 'radio',
                            'multiple': 'checkbox',
                            'boolean': 'yesno',
                            'long_text': 'textarea',
                        }
                        qtype = type_map.get(str(qtype).lower(), str(qtype).lower())

                        options = (
                            q.get('options')
                            or q.get('choices')
                            or q.get('option')
                            or q.get('values')
                            or q.get('data')
                            or []
                        )
                        required = bool(q.get('required') or q.get('is_required') or q.get('mandatory'))

                        normalized_questions.append({
                            'text': text,
                            'type': qtype,
                            'options': options,
                            'required': required,
                        })

                    questions_from_json = normalized_questions

                    # Preload existing answers mapped by question text for JSON mode
                    related_questions = Question.objects.filter(survey=survey)
                    question_text_to_id = {q.question_text: q.id for q in related_questions}
                    if question_text_to_id:
                        for qtext, qid in question_text_to_id.items():
                            ans = Answer.objects.filter(survey_response=survey_response, question_id=qid).first()
                            if ans and ans.answer_text is not None:
                                existing_answers_json[qtext] = ans.answer_text
            except Exception as e:
                logger.error(f"Error reading survey JSON: {str(e)}")
                messages.error(request, "Error loading survey questions")
        
        # Fallback to database questions if no JSON
        questions_from_db = Question.objects.filter(survey=survey).order_by('order')
        
        # Handle form submission
        if request.method == 'POST':
            submit_action = request.POST.get('submit_action', 'submit')
            # Process answers from JSON questions
            if questions_from_json:
                for idx, q in enumerate(questions_from_json):
                    # Normalize text and type
                    qtext = (
                        q.get('text')
                        or q.get('question')
                        or q.get('question_text')
                        or q.get('label')
                        or q.get('title')
                        or f'Question {idx+1}'
                    )
                    qtype = (
                        q.get('type')
                        or q.get('question_type')
                        or ('radio' if (q.get('options') or q.get('choices') or q.get('option') or q.get('values') or q.get('data')) else 'text')
                    )
                    options = (
                        q.get('options')
                        or q.get('choices')
                        or q.get('option')
                        or q.get('values')
                        or q.get('data')
                        or []
                    )

                    # Ensure a matching Question exists for storing Answer records
                    question_obj, _ = Question.objects.get_or_create(
                        survey=survey,
                        question_text=qtext,
                        defaults={
                            'question_type': qtype if qtype in dict(Question.QUESTION_TYPES) else 'text',
                            'options': options if isinstance(options, list) else [],
                            'order': idx,
                            'is_required': bool(q.get('required') or q.get('is_required') or q.get('mandatory')),
                        }
                    )

                    # Read answer(s) from POST
                    name_key = f'question_{idx}'
                    if str(qtype).lower() == 'checkbox':
                        selected = request.POST.getlist(name_key)
                        answer_value = ', '.join(selected)
                    else:
                        answer_value = request.POST.get(name_key, '')

                    # Save or update Answer
                    Answer.objects.update_or_create(
                        survey_response=survey_response,
                        question=question_obj,
                        defaults={'answer_text': answer_value}
                    )

                # Update completion state based on action
                if submit_action == 'save':
                    survey_response.is_completed = False
                else:
                    survey_response.is_completed = True
                    survey_response.completed_at = timezone.now()
                survey_response.save()
                
            else:
                # Process answers from database questions
                for question in questions_from_db:
                    # For DB questions, support checkboxes via getlist
                    key = f'question_{question.id}'
                    if question.question_type == 'checkbox':
                        selected = request.POST.getlist(key)
                        answer_text = ', '.join(selected)
                    else:
                        answer_text = request.POST.get(key, '')
                    
                    # Save or update answer
                    answer, created = Answer.objects.update_or_create(
                        survey_response=survey_response,
                        question=question,
                        defaults={'answer_text': answer_text}
                    )
                
                # Update completion state based on action
                if submit_action == 'save':
                    survey_response.is_completed = False
                else:
                    survey_response.is_completed = True
                    survey_response.completed_at = timezone.now()
                survey_response.save()
            
            # On save, keep user on the page; on submit, go to done page
            if submit_action == 'save':
                # If AJAX autosave, return JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({ 'status': 'saved' })
                messages.success(request, "Draft saved")
                return redirect('survey_detail', survey_id=survey.id)
            else:
                messages.success(request, "Survey completed successfully")
                return redirect('survey_done', response_id=survey_response.id)
        
        # Get existing answers if any
        existing_answers = {}
        for answer in Answer.objects.filter(survey_response=survey_response):
            existing_answers[answer.question.id] = answer.answer_text
        
        context = {
            'doctor': doctor,
            'survey': survey,
            'questions': questions_from_db,  # Database questions (fallback)
            'questions_json': questions_from_json,  # JSON questions
            'existing_answers': existing_answers,
            'survey_json_data': survey_json_data,
            'existing_answers_json': existing_answers_json,
            'view_mode': view_mode
        }
        
        return render(request, 'wtestapp/survey_detail.html', context)
    
    except (CustomUser.DoesNotExist, Doctor.DoesNotExist) as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('login')

def survey_done(request, response_id):
    """View to display after survey completion"""
    if 'mobile' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    try:
        doctor = None
        doctor_id = request.session.get('doctor_id')
        if doctor_id:
            doctor = Doctor.objects.get(id=doctor_id)
        else:
            mobile = request.session.get('mobile')
            if mobile:
                try:
                    doctor = Doctor.objects.get(mobile=mobile)
                except Doctor.DoesNotExist:
                    custom_user = CustomUser.objects.get(mobile=mobile)
                    doctor = Doctor.objects.get(custom_user=custom_user)
        if not doctor:
            raise Doctor.DoesNotExist("Doctor not found in session context")
        survey_response = get_object_or_404(SurveyResponse, id=response_id, doctor=doctor)
        
        context = {
            'doctor': doctor,
            'survey_response': survey_response,
            'survey': survey_response.survey
        }
        
        return render(request, 'wtestapp/survey_done.html', context)
    
    except (CustomUser.DoesNotExist, Doctor.DoesNotExist):
        messages.error(request, "User or doctor profile not found")
        return redirect('login')

def index(request):
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from .models import CustomUser, Doctor, Survey, Agreement
import random

def get_user_completion_status(doctor):
    """Check what tasks are pending for a doctor"""
    pending_tasks = []
    redirect_url = None
    
    profile_complete = all([
        doctor.first_name,
        doctor.last_name,
        doctor.email,
        doctor.profession,
        doctor.specialty
    ])
    
    if not profile_complete:
        pending_tasks.append('Profile is incomplete')
        if not redirect_url:
            redirect_url = 'doctor_profile'
    
    agreement_signed = Agreement.objects.filter(doctor=doctor, signed_at__isnull=False).exists()
    if not agreement_signed:
        pending_tasks.append('Please review and sign the agreement to proceed')
        if not redirect_url:
            assigned_survey = Survey.objects.filter(assigned_to=doctor).order_by('-created_at').first()
            if assigned_survey:
                redirect_url = ('agreement_page', {'survey_id': assigned_survey.id})
            else:
                redirect_url = 'doctor_profile'
    
    assigned_surveys = Survey.objects.filter(assigned_to=doctor)
    completed_surveys = SurveyResponse.objects.filter(doctor=doctor, is_completed=True).values_list('survey_id', flat=True)
    pending_surveys = assigned_surveys.exclude(id__in=completed_surveys)
    
    if pending_surveys.exists():
        pending_tasks.append('Complete your pending surveys to finish your registration')
        if not redirect_url:
            redirect_url = ('survey_detail', {'survey_id': pending_surveys.first().id})
    
    return {
        'has_pending': len(pending_tasks) > 0,
        'pending_tasks': pending_tasks,
        'redirect_url': redirect_url,
        'all_complete': len(pending_tasks) == 0
    }

def login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        if mobile and len(mobile) == 10 and mobile.isdigit():
            # Generate a 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Store mobile and OTP in session
            request.session['mobile'] = mobile
            request.session['otp'] = otp
            
            # For development, print OTP to console and show success message
            print(f"OTP for {mobile}: {otp}")
            messages.success(request, f'OTP sent to {mobile}')
            
            # Add debug message to display OTP on page
            messages.info(request, f'For testing: Your OTP is {otp}')
            
            return redirect('verify_otp')
        else:
            messages.error(request, 'Please enter a valid 10-digit mobile number')
    
    return render(request, 'wtestapp/login.html')

def verify_otp(request):
    mobile = request.session.get('mobile')
    if not mobile:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        
        if otp == stored_otp:
            try:
                # Step 1: Get or create CustomUser
                custom_user, user_created = CustomUser.objects.get_or_create(
                    mobile=mobile,
                    defaults={'username': mobile}
                )
                
                # Step 2: Check if Doctor already exists for this mobile
                try:
                    doctor = Doctor.objects.get(mobile=mobile)
                except Doctor.DoesNotExist:
                    # Step 3: If Doctor doesn't exist, create one
                    doctor = Doctor.objects.create(
                        mobile=mobile,
                        custom_user=custom_user
                    )
                
                # Step 4: Set session variables
                request.session['doctor_id'] = doctor.id
                request.session['is_verified'] = True
                
                # Step 5: Clear OTP from session after successful verification
                if 'otp' in request.session:
                    del request.session['otp']
                
                # Step 6: Check completion status and redirect accordingly
                status = get_user_completion_status(doctor)
                
                if status['all_complete']:
                    return redirect('doctor_profile_view')
                else:
                    request.session['pending_tasks'] = status['pending_tasks']
                    if isinstance(status['redirect_url'], tuple):
                        url_name, kwargs = status['redirect_url']
                        return redirect(url_name, **kwargs)
                    else:
                        return redirect(status['redirect_url'])
            except Exception as e:
                messages.error(request, f'Error creating profile: {str(e)}. Please try again.')
                print(f"Error in verify_otp: {str(e)}")
                import traceback
                traceback.print_exc()
                return redirect('verify_otp')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            
    return render(request, 'wtestapp/verify_otp.html', {'mobile': mobile})

def doctor_profile(request):
    # Get doctor from session
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        messages.error(request, 'Please login first')
        return redirect('login')
        
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        
        pending_tasks = request.session.get('pending_tasks', [])
        if pending_tasks:
            for task in pending_tasks:
                messages.warning(request, task)
            del request.session['pending_tasks']
        
        if request.method == 'POST':
            # Personal Details
            doctor.first_name = request.POST.get('first_name', '')
            doctor.last_name = request.POST.get('last_name', '')
            doctor.email = request.POST.get('email', '')
            doctor.gender = request.POST.get('gender', '')
            date_of_birth = request.POST.get('date_of_birth', '')
            if date_of_birth:
                doctor.date_of_birth = date_of_birth
            
            # Address
            doctor.address = request.POST.get('address', '')
            doctor.state = request.POST.get('state', '')
            doctor.city = request.POST.get('city', '')
            doctor.pincode = request.POST.get('pincode', '')
            
            # Professional Details
            doctor.profession = request.POST.get('profession', '')
            doctor.specialty = request.POST.get('specialty', '')
            doctor.degree = request.POST.get('degree', '')
            doctor.mci_registration = request.POST.get('mci_registration', '')
            doctor.pan = request.POST.get('pan', '')
            
            # GST Information
            has_gst = request.POST.get('has_gst', 'false')
            doctor.has_gst = (has_gst == 'true')
            if doctor.has_gst:
                doctor.gst_number = request.POST.get('gst_number', '')
                # GST Certificate upload
                if 'gst_certificate' in request.FILES:
                    doctor.gst_certificate = request.FILES['gst_certificate']
            else:
                doctor.gst_number = ''
            
            # File Uploads - Common for both GC and CP
            if 'pan_copy' in request.FILES:
                doctor.pan_copy = request.FILES['pan_copy']
            
            # Cancelled Cheque - Only for CP (Critical Patient)
            if doctor.portal_type == 'CP' and 'cancelled_cheque' in request.FILES:
                doctor.cancelled_cheque = request.FILES['cancelled_cheque']
            
            # Prescription - Common for both GC and CP
            if 'prescription_file' in request.FILES:
                doctor.prescription_file = request.FILES['prescription_file']
            
            doctor.save()
            
            messages.success(request, 'Profile saved successfully! Please review and sign the agreement.')

            # Redirect to agreement page
            # If an Agreement already exists for this doctor, prefer its survey
            existing_agreement = Agreement.objects.filter(doctor=doctor).first()
            if existing_agreement and existing_agreement.survey:
                return redirect('agreement_page', survey_id=existing_agreement.survey.id)

            # Otherwise prefer a survey explicitly assigned to this doctor
            assigned_survey = (
                Survey.objects.filter(assigned_to=doctor)
                .order_by('-created_at')
                .first()
            )

            # Fallback: pick the most recent survey for this portal type
            if not assigned_survey and doctor.portal_type:
                assigned_survey = (
                    Survey.objects.filter(portal_type=doctor.portal_type)
                    .order_by('-created_at')
                    .first()
                )

            if not assigned_survey:
                messages.error(request, 'No survey found. Please ask admin to create/assign a survey.')
                return redirect('doctor_profile')

            # Redirect to the agreement page using the chosen survey
            return redirect('agreement_page', survey_id=assigned_survey.id)
            
        return render(request, 'wtestapp/doctor_profile.html', {'doctor': doctor})
        
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        print(f"Error in doctor_profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect('login')

def doctor_profile_view(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('login')
    
    doctor = Doctor.objects.get(id=doctor_id)
    
    status = get_user_completion_status(doctor)
    
    if status['has_pending']:
        for task in status['pending_tasks']:
            messages.info(request, task)
    
    completed_surveys = SurveyResponse.objects.filter(doctor=doctor, is_completed=True).order_by('-completed_at')
    agreement = Agreement.objects.filter(doctor=doctor).first()
    
    return render(request, 'wtestapp/doctor_profile_view.html', {
        'doctor': doctor,
        'completed_surveys': completed_surveys,
        'agreement': agreement
    })

def doctor_profile_edit(request):
    doctor_id = request.session.get('doctor_id')
    if not doctor_id:
        return redirect('login')
    
    doctor = Doctor.objects.get(id=doctor_id)
    
    if request.method == 'POST':
        # Update doctor profile fields
        doctor.name = request.POST.get('name')
        doctor.email = request.POST.get('email')
        doctor.specialization = request.POST.get('specialization')
        doctor.hospital_name = request.POST.get('hospital_name')
        doctor.city = request.POST.get('city')
        doctor.medical_registration_no = request.POST.get('medical_registration_no')
        doctor.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('doctor_profile')
        
    return render(request, 'wtestapp/doctor_profile_edit.html', {'doctor': doctor})

def agreement_page(request, survey_id):
    if 'mobile' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    try:
        doctor_id = request.session.get('doctor_id')
        if doctor_id:
            doctor = Doctor.objects.get(id=doctor_id)
            
            pending_tasks = request.session.get('pending_tasks', [])
            if pending_tasks:
                for task in pending_tasks:
                    messages.warning(request, task)
                del request.session['pending_tasks']
        else:
            # Fallbacks for older sessions
            mobile = request.session.get('mobile')
            if not mobile:
                raise Doctor.DoesNotExist("Missing mobile in session")
            # Get via Doctor.mobile first (matches verify_otp flow)
            try:
                doctor = Doctor.objects.get(mobile=mobile)
            except Doctor.DoesNotExist:
                # As a last resort, map CustomUser -> Doctor via OneToOneField
                custom_user = CustomUser.objects.get(mobile=mobile)
                doctor = Doctor.objects.get(custom_user=custom_user)
        survey = Survey.objects.get(id=survey_id)
        
        # Check if agreement already exists (by doctor only, OneToOne)
        existing_agreement = Agreement.objects.filter(doctor=doctor).first()
        # If admin has linked a specific survey in Agreement, use it for display
        if existing_agreement and existing_agreement.survey:
            survey = existing_agreement.survey
        
        if request.method == 'POST':
            if 'signature_data' in request.POST and request.POST['signature_data']:
                # One agreement per doctor due to OneToOne; attach current survey and amount
                agreement, _ = Agreement.objects.get_or_create(doctor=doctor)
                agreement.survey = survey
                agreement.agreement_text = 'Agreement signed'
                agreement.digital_signature = request.POST.get('signature_data', '')
                agreement.signature_type = request.POST.get('signature_type', 'drawn')
                agreement.signed_at = timezone.now()
                # If admin pre-set an amount in Agreement, keep it; else use survey amount
                agreement.amount = existing_agreement.amount if (existing_agreement and existing_agreement.amount) else survey.amount
                agreement.save()
                
                # Update doctor's agreement status
                doctor.agreement_accepted = True
                doctor.save()
                
                messages.success(request, 'Agreement accepted successfully!')
                # Go directly to the survey so the uploaded JSON/questions show immediately
                return redirect('survey_detail', survey_id=survey.id)
            else:
                messages.error(request, 'Please provide a valid signature')
        
        # Get amount and survey title, preferring Agreement.amount if set
        amount = existing_agreement.amount if (existing_agreement and existing_agreement.amount) else survey.amount
        survey_title = survey.title
        
        # Get current date in the required format
        current_date = timezone.now()
        
        return render(request, 'wtestapp/agreement_page.html', {
            'doctor': doctor,
            'survey': survey,
            'amount': amount,
            'existing_agreement': existing_agreement,
            'signed_date': current_date,
            'default_signed_date': current_date.strftime('%d/%m/%Y'),
            'survey_title': survey_title
        })
        
    except (Doctor.DoesNotExist, Survey.DoesNotExist) as e:
        messages.error(request, 'Doctor or survey not found')
        return redirect('doctor_profile')
    except Exception as e:
        messages.error(request, f'Error loading agreement: {str(e)}')
        return redirect('doctor_profile')

def gc_profile(request):
    """View for GC role profile"""
    mobile = request.session.get('mobile')
    if not mobile:
        return redirect('login')
        
    try:
        user = CustomUser.objects.get(mobile=mobile)
        doctor = Doctor.objects.get(mobile=mobile)
    except (CustomUser.DoesNotExist, Doctor.DoesNotExist):
        return redirect('login')
        
    if user.role != 'gc':
        messages.error(request, 'You do not have access to this page.')
        return redirect('doctor_profile')
        
    return render(request, 'wtestapp/gc_profile.html', {'doctor': doctor, 'user': user})
    
def cp_profile(request):
    """View for CP role profile"""
    mobile = request.session.get('mobile')
    if not mobile:
        return redirect('login')
        
    try:
        user = CustomUser.objects.get(mobile=mobile)
        doctor = Doctor.objects.get(mobile=mobile)
    except (CustomUser.DoesNotExist, Doctor.DoesNotExist):
        return redirect('login')
        
    if user.role != 'cp':
        messages.error(request, 'You do not have access to this page.')
        return redirect('doctor_profile')
        
    return render(request, 'wtestapp/cp_profile.html', {'doctor': doctor, 'user': user})



def download_survey_pdf(request, response_id):
    """View to download a survey response as PDF"""
    if 'doctor_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    try:
        # Get the survey response
        survey_response = get_object_or_404(SurveyResponse, id=response_id)
        
        # Security check - only allow the doctor who completed the survey to download it
        if survey_response.doctor.id != request.session['doctor_id']:
            messages.error(request, "You don't have permission to download this survey")
            return redirect('surveys')
        
        # If the PDF is already generated, return it
        if survey_response.pdf_file:
            response = HttpResponse(survey_response.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="survey_{response_id}.pdf"'
            return response
        else:
            # Generate PDF on the fly
            from django.template.loader import render_to_string
            from xhtml2pdf import pisa
            from io import BytesIO
            
            # Get all answers for this survey response
            answers = Answer.objects.filter(survey_response=survey_response)
            
            # Prepare context for PDF template
            context = {
                'survey': survey_response.survey,
                'doctor': survey_response.doctor,
                'answers': answers,
                'completed_at': survey_response.completed_at,
            }
            
            # Render HTML content
            html_string = render_to_string('wtestapp/survey_pdf_template.html', context)
            
            # Create PDF
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
            
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="survey_{response_id}.pdf"'
                return response
            else:
                return HttpResponse("Error generating PDF", status=500)
    
    except Exception as e:
        messages.error(request, f"Error downloading survey: {str(e)}")
        return redirect('surveys')

def request_agreement_otp(request):
    """Send OTP before downloading agreement PDF"""
    if 'doctor_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        
        import random
        otp = str(random.randint(100000, 999999))
        
        request.session['agreement_otp'] = otp
        request.session['agreement_otp_time'] = timezone.now().isoformat()
        
        mobile = doctor.mobile
        message = f"Your OTP to download agreement is: {otp}. Valid for 5 minutes."
        
        sms_sent = send_sms(mobile, message)
        
        if sms_sent:
            return JsonResponse({
                'success': True, 
                'message': f'OTP sent to {mobile}',
                'mobile': mobile,
                'otp': otp
            })
        else:
            return JsonResponse({'success': False, 'message': 'Failed to send OTP'})
            
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Doctor not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def verify_agreement_otp(request):
    """Verify OTP and allow PDF download"""
    if 'doctor_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        stored_otp = request.session.get('agreement_otp')
        otp_time_str = request.session.get('agreement_otp_time')
        
        if not stored_otp or not otp_time_str:
            return JsonResponse({'success': False, 'message': 'No OTP found. Please request a new one'})
        
        from datetime import datetime, timedelta
        otp_time = datetime.fromisoformat(otp_time_str)
        
        if timezone.now() - otp_time > timedelta(minutes=5):
            del request.session['agreement_otp']
            del request.session['agreement_otp_time']
            return JsonResponse({'success': False, 'message': 'OTP expired. Please request a new one'})
        
        if entered_otp == stored_otp:
            request.session['agreement_verified'] = True
            del request.session['agreement_otp']
            del request.session['agreement_otp_time']
            return JsonResponse({'success': True, 'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def download_agreement(request):
    """View to download the agreement PDF"""
    if 'doctor_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    if not request.session.get('agreement_verified'):
        messages.error(request, "Please verify OTP first")
        return redirect('doctor_profile_view')
    
    del request.session['agreement_verified']
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        agreement = Agreement.objects.filter(doctor=doctor).first()
        
        if agreement and agreement.pdf_file:
            response = HttpResponse(agreement.pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="agreement.pdf"'
            return response
        else:
            # If no specific agreement file, generate a default one
            from django.template.loader import render_to_string
            from xhtml2pdf import pisa
            from io import BytesIO
            import os
            from django.conf import settings
            
            # Get the latest survey for amount and title
            survey = Survey.objects.filter(assigned_to=doctor).order_by('-created_at').first()
            if not survey:
                # Fallback: get any survey for this doctor's portal type
                if doctor.portal_type:
                    survey = Survey.objects.filter(portal_type=doctor.portal_type).order_by('-created_at').first()
            
            amount = survey.amount if survey else 20000  # Default amount
            survey_title = survey.title if survey else "Inclinic experience of Topical Sunscreen in Paediatric"
            
            # Get current date
            current_date = timezone.now()
            
            # Prepare logo and signature paths - use absolute file paths for PDF generation
            import os
            from django.conf import settings
            
            # Get absolute file paths for PDF generation
            logo_file_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'logo', 'logo.png')
            sig_file_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'logo', 'sig.png')
            
            # Check if files exist and use absolute paths
            logo_path = logo_file_path if os.path.exists(logo_file_path) else None
            sig_path = sig_file_path if os.path.exists(sig_file_path) else None
            
            # Get doctor's signature if agreement exists
            doctor_sig_path = None
            if agreement and agreement.digital_signature:
                # digital_signature is base64 encoded
                sig_data = agreement.digital_signature
                # If it already has the data URI prefix, use as-is; otherwise add it
                if not sig_data.startswith('data:image'):
                    # Remove any existing prefix before adding new one
                    if ',' in sig_data:
                        sig_data = sig_data.split(',', 1)[1]
                    doctor_sig_path = f"data:image/png;base64,{sig_data}"
                else:
                    doctor_sig_path = sig_data
            
            # Render agreement template to HTML
            html = render_to_string('wtestapp/agreement_pdf_template.html', {
                'doctor': doctor,
                'amount': amount,
                'survey_title': survey_title,
                'signed_date': current_date,
                'default_signed_date': current_date.strftime('%d/%m/%Y'),
                'logo_path': logo_path,
                'sig_path': sig_path,
                'doctor_sig_path': doctor_sig_path
            })
            
            # Convert HTML to PDF
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
            
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="agreement.pdf"'
                return response
            else:
                messages.error(request, "Error generating agreement PDF")
                return redirect('doctor_profile_view')
            
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error downloading agreement: {str(e)}")
        return redirect('doctor_profile_view')

def get_doctor_survey_api(request):
    """API to get doctor's survey ID for agreement"""
    if 'doctor_id' not in request.session:
        return JsonResponse({'success': False, 'message': 'Not logged in'})
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        
        existing_agreement = Agreement.objects.filter(doctor=doctor).first()
        if existing_agreement and existing_agreement.survey:
            return JsonResponse({'success': True, 'survey_id': existing_agreement.survey.id})
        
        assigned_survey = Survey.objects.filter(assigned_to=doctor).order_by('-created_at').first()
        
        if not assigned_survey and doctor.portal_type:
            assigned_survey = Survey.objects.filter(portal_type=doctor.portal_type).order_by('-created_at').first()
        
        if assigned_survey:
            return JsonResponse({'success': True, 'survey_id': assigned_survey.id})
        else:
            return JsonResponse({'success': False, 'message': 'No survey found'})
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Doctor not found'})

def sign_agreement(request):
    """View to handle agreement signing"""
    if 'doctor_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('login')
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        
        if request.method == 'POST':
            signature_data = request.POST.get('signature')
            if not signature_data:
                messages.error(request, "Please provide your signature")
                return redirect('doctor_profile_view')
            
            # Get or create agreement
            agreement, created = Agreement.objects.get_or_create(doctor=doctor)
            
            # Update agreement details
            agreement.digital_signature = signature_data
            agreement.signed_at = timezone.now()
            agreement.save()
            
            # Update doctor's agreement status
            doctor.agreement_accepted = True
            doctor.save()
            
            messages.success(request, "Agreement signed successfully!")
            return redirect('doctor_profile_view')
        
        # For GET request, show signature page
        return render(request, 'wtestapp/sign_agreement.html', {'doctor': doctor})
        
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error signing agreement: {str(e)}")
        return redirect('doctor_profile_view')


