from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.urls import reverse # Import reverse
from django.http import HttpResponse, JsonResponse # Import HttpResponse, JsonResponse
from django.template.loader import get_template # Import get_template
from django.utils import timezone
from django.conf import settings # Import settings
from django.contrib.staticfiles.finders import find # Import find
from xhtml2pdf import pisa # Import pisa
from io import BytesIO # Import BytesIO
import os # Import os
import json
import pandas as pd
from django.db import models, transaction # Re-add transaction

from .models import Doctor, Survey, Question, Answer, Agreement, SurveyResponse
from .forms import SurveyUploadForm, DoctorProfileForm

# Utility function to handle static files for xhtml2pdf
def link_callback(uri, rel):
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /full/path/to/static/
    mUrl = settings.MEDIA_URL       # Typically /media/
    mRoot = settings.MEDIA_ROOT     # Typically /full/path/to/media/

    print(f"DEBUG: link_callback called with uri: {uri}, rel: {rel}")
    print(f"DEBUG: settings.STATIC_URL: {sUrl}, settings.STATIC_ROOT: {sRoot}")
    print(f"DEBUG: settings.MEDIA_URL: {mUrl}, settings.MEDIA_ROOT: {mRoot}")

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
        print(f"DEBUG: Resolved path (media): {path}")
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
        print(f"DEBUG: Resolved path (static 1): {path}")
        if not os.path.exists(path):
            path = find(uri.replace(sUrl, ''))
            print(f"DEBUG: Resolved path (static 2 - find): {path}")
    else:
        print(f"DEBUG: URI not starting with static/media URL: {uri}")
        return uri

    if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
    return path


def index(request):
    return redirect('login')


def _get_portal_from_request(request):
    path = request.path.lower()
    if path.startswith('/cp/'):
        return 'CP'
    if path.startswith('/gc/'):
        return 'GC'
    return None


def login(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        if mobile:
            username = f"doctor_{mobile}"
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_unusable_password()
                user.save()
            
            # Store mobile and portal in session to pass to verify_otp for Doctor object update
            request.session['mobile'] = mobile
            request.session['username'] = username
            portal = _get_portal_from_request(request)
            if portal:
                request.session['portal_type'] = portal

            messages.success(request, f'OTP sent to {mobile}. (Simulated OTP: 1234)')
            return redirect('verify_otp')
        else:
            messages.error(request, 'Mobile number is required.')
    return render(request, 'wtestapp/login.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == '1234':
            mobile = request.session.get('mobile')
            username = request.session.get('username')
            portal = request.session.get('portal_type')
            if mobile and username:
                user = User.objects.get(username=username)

                auth_login(request, user)

                # Ensure Doctor object exists or is created here, with mobile updated
                doctor, created = Doctor.objects.get_or_create(
                    user=user,
                    defaults={'mobile': mobile} # Ensure mobile is set on creation
                )
                if not created and doctor.mobile != mobile:
                    doctor.mobile = mobile
                # Set portal_type if not set
                if portal and (doctor.portal_type != portal):
                    doctor.portal_type = portal
                doctor.save()

                # Initialize agreement amount rotation for new users: start at Rs 2000
                if created:
                    request.session['agreement_amount_index'] = 1  # 0=>1000, 1=>2000, 2=>25000

                if 'mobile' in request.session: del request.session['mobile']
                if 'username' in request.session: del request.session['username']
                if 'portal_type' in request.session: del request.session['portal_type']

                messages.success(request, 'Login successful!')
                return redirect('doctor_profile') # Always redirect to doctor_profile for initial check
            else:
                messages.error(request, 'Session data missing. Please try logging in again.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid OTP.')
    return render(request, 'wtestapp/otp.html')


@login_required
def doctor_profile(request):
    # This view acts as a gateway to either view or edit the profile
    try:
        doctor = Doctor.objects.get(user=request.user)
        # First: Check profile completeness
        if not all([
            doctor.first_name, doctor.last_name, doctor.email, doctor.mobile,
            doctor.address, doctor.specialty, doctor.mci_registration, doctor.pan
        ]):
            messages.info(request, "Please complete your doctor profile.")
            return redirect('doctor_profile_edit')

        # Second: If profile is complete, check agreement
        if not doctor.agreement_accepted:
            return redirect('agreement_page')

        # Finally: everything ok, show profile view
        return redirect('doctor_profile_view')
    except Doctor.DoesNotExist:
        # If Doctor object doesn't exist, it means a new user logged in
        messages.info(request, "Please create your doctor profile.")
        return redirect('doctor_profile_edit')


@login_required
def doctor_profile_view(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        # This should ideally not happen if doctor_profile redirects correctly
        messages.error(request, "Doctor profile not found. Please complete your profile.")
        return redirect('doctor_profile_edit')
        
    context = {'doctor': doctor}
    return render(request, 'wtestapp/doctor_profile_view.html', context)


@login_required
def doctor_profile_edit(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = Doctor(user=request.user)  # Create a new unsaved Doctor instance

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            # Custom handling for has_gst = False to clear gst_number
            if not form.cleaned_data.get('has_gst'):
                doctor.gst_number = ''
            # If profession left blank, default to 'Doctor'
            if not form.cleaned_data.get('profession'):
                doctor.profession = 'Doctor'
            # Ensure mobile is populated: try existing, posted, or derive from username
            if not doctor.mobile:
                posted_mobile = request.POST.get('mobile')
                if posted_mobile:
                    doctor.mobile = posted_mobile
                else:
                    uname = request.user.username or ''
                    if uname.startswith('doctor_') and len(uname) > 7:
                        doctor.mobile = uname.split('doctor_', 1)[1]
            form.save()
            messages.success(request, 'Profile updated successfully!')
            # After saving profile, proceed to Agreement page
            return redirect('agreement_page')
    else:
        form = DoctorProfileForm(instance=doctor)

    context = {'form': form, 'doctor': doctor}
    return render(request, 'wtestapp/doctor_profile.html', context)


@login_required
def doctor_profile_gc(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        doctor = Doctor(user=request.user)

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            if not form.cleaned_data.get('has_gst'):
                doctor.gst_number = ''
            if not form.cleaned_data.get('profession'):
                doctor.profession = 'Doctor'
            if not doctor.mobile:
                posted_mobile = request.POST.get('mobile')
                if posted_mobile:
                    doctor.mobile = posted_mobile
                else:
                    uname = request.user.username or ''
                    if uname.startswith('doctor_') and len(uname) > 7:
                        doctor.mobile = uname.split('doctor_', 1)[1]
            form.save()
            messages.success(request, 'Profile (GC) updated successfully!')
            return redirect('agreement_page')
    else:
        form = DoctorProfileForm(instance=doctor)

    context = {'form': form, 'doctor': doctor}
    return render(request, 'wtestapp/doctor_profile_gc.html', context)


@login_required
def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    doctor = get_object_or_404(Doctor, user=request.user)

    # Debugging: Print survey details and questions queryset
    print(f"--- Debug: survey_detail view ---")
    print(f"Survey ID: {survey.id}, Title: {survey.title}")
    questions_queryset = survey.questions.all()
    print(f"Questions Queryset: {questions_queryset}")
    print(f"Number of questions: {questions_queryset.count()}")
    for q in questions_queryset:
        print(f"  Question ID: {q.id}, Text: {q.question_text}, Type: {q.question_type}, Options: {q.options}")
    print(f"----------------------------------")

    # Check if the doctor is assigned to this survey
    if not doctor.surveys.filter(id=survey_id).exists():
        messages.error(request, "You are not assigned to this survey.")
        return redirect('doctor_surveys_list')

    # Ensure or create a SurveyResponse for this doctor and survey
    survey_response, _ = SurveyResponse.objects.get_or_create(doctor=doctor, survey=survey)

    if request.method == 'POST':
        submit_action = request.POST.get('submit_action', 'submit')
        # Allow user to clear any saved answers so nothing is pre-selected
        if submit_action == 'reset':
            Answer.objects.filter(survey_response=survey_response).delete()
            messages.success(request, "Selections cleared.")
            return redirect('survey_detail', survey_id=survey.id)
        for question in survey.questions.all():
            if question.question_type == 'checkbox':
                answer_values = request.POST.getlist(f'question_{question.id}')
                answer_text = ", ".join(answer_values)
            else:
                answer_text = request.POST.get(f'question_{question.id}')

            if answer_text is not None:
                Answer.objects.update_or_create(
                    question=question,
                    survey_response=survey_response,
                    defaults={'answer_text': answer_text}
                )
        if submit_action == 'submit':
            # Mark response as completed
            survey_response.is_completed = True
            survey_response.completed_at = timezone.now()
            survey_response.save()
            messages.success(request, "Survey submitted successfully!")
            # Remember last survey URL for Thank You page button
            request.session['last_survey_url'] = reverse('survey_detail', args=[survey.id])
            return redirect('survey_done')
        else:
            messages.success(request, "Survey saved. You can continue later.")
            # Fall through to re-render the page with prefilled answers

    # Prefill answers map for template
    existing_answers = {a.question_id: a.answer_text for a in Answer.objects.filter(survey_response=survey_response)}
    context = {
        'survey': survey,
        'questions': questions_queryset,
        'answers_map': existing_answers,
    }
    return render(request, 'wtestapp/survey_detail.html', context)


@login_required
def survey_done(request):
    last_url = request.session.get('last_survey_url')
    context = { 'last_survey_url': last_url }
    return render(request, 'wtestapp/survey_done.html', context)


@login_required
def doctor_surveys_list(request):
    # Only allow access if profile is complete and agreement accepted
    doctor, _ = Doctor.objects.get_or_create(user=request.user)
    # Check profile completeness
    if not all([
        doctor.first_name, doctor.last_name, doctor.email, doctor.mobile,
        doctor.address, doctor.specialty, doctor.mci_registration, doctor.pan
    ]):
        messages.info(request, "Please complete your doctor profile before accessing surveys.")
        return redirect('doctor_profile_edit')
    # Check agreement acceptance
    if not doctor.agreement_accepted:
        messages.info(request, "Please accept the participant agreement before accessing surveys.")
        return redirect('agreement_page')
    assigned_surveys = doctor.surveys.all()
    # Filter by portal if doctor has a portal set
    if doctor.portal_type:
        assigned_surveys = assigned_surveys.filter(portal_type=doctor.portal_type)

    context = {
        'doctor': doctor,
        'surveys': assigned_surveys,
        'last_survey_url': request.session.get('last_survey_url'),
    }
    return render(request, 'wtestapp/doctor_surveys.html', context)


@login_required
def survey1(request):
    """Session-based dummy survey with fixed questions; no backend models.
    Saves answers in session under 'survey1_answers'.
    """
    answers = request.session.get('survey1_answers', {
        'q1': '', 'q2': '', 'q3': [], 'q3_other': '', 'q4': [], 'q5': '', 'q5_detail': '', 'q6': '', 'q7': '', 'q8': ''
    })

    if request.method == 'POST':
        action = request.POST.get('submit_action', 'save')
        if action == 'reset':
            request.session['survey1_answers'] = {
                'q1': '', 'q2': '', 'q3': [], 'q3_other': '', 'q4': [], 'q5': '', 'q5_detail': '', 'q6': '', 'q7': '', 'q8': ''
            }
            messages.success(request, 'Selections cleared.')
            return redirect('survey1')

        # Collect answers
        new_answers = {
            'q1': request.POST.get('q1', ''),
            'q2': request.POST.get('q2', ''),
            'q3': request.POST.getlist('q3'),
            'q3_other': request.POST.get('q3_other', ''),
            'q4': request.POST.getlist('q4'),
            'q5': request.POST.get('q5', ''),
            'q5_detail': request.POST.get('q5_detail', ''),
            'q6': request.POST.get('q6', ''),
            'q7': request.POST.get('q7', ''),
            'q8': request.POST.get('q8', ''),
        }
        request.session['survey1_answers'] = new_answers
        request.session.modified = True

        if action == 'submit':
            messages.success(request, 'Survey submitted successfully!')
            # Remember last survey URL for Thank You page
            request.session['last_survey_url'] = reverse('survey1')
            return redirect('survey_done')
        else:
            messages.success(request, 'Draft saved.')

    q1_opts = ["Always","Often","Sometimes","Rarely","Never"]
    q2_opts = [
        "above 6 months","Above 1 years","Above 3 years",
        "Depends on the skin condition","I do not recommend sunscreen for babies"
    ]
    q3_opts = [
        "Routine outdoor exposure","Atopic or sensitive skin",
        "During vacations/travel to sunny regions","Family history of photodermatoses",
        "Post-treatment for skin conditions (e.g., after topical steroids)",
        "To prevent tanning or pigmentation"
    ]
    q4_opts = [
        "Mineral/physical filters (zinc oxide, titanium dioxide)",
        "Fragrance-free formulation","Water resistance",
        "Broad-spectrum protection (UVA/UVB)","SPF value"
    ]
    q6_opts = ["Very receptive","Somewhat receptive","Indifferent","Resistant"]
    q8_opts = ["Cream","Lotion","Gel","Spray","Stick"]

    context = {
        'answers': request.session.get('survey1_answers', answers),
        'q1_opts': q1_opts,
        'q2_opts': q2_opts,
        'q3_opts': q3_opts,
        'q4_opts': q4_opts,
        'q6_opts': q6_opts,
        'q8_opts': q8_opts,
    }
    return render(request, 'wtestapp/survey1.html', context)


@login_required
def survey2(request):
    """Session-based dummy survey 2 (Anaemia) using the same UI pattern as survey1."""
    # Define questions schema
    questions = [
        { 'name': 'q1', 'title': 'What percent women present with Moderate (Hb 7-9.9 gm/dl) or Severe (Hb <6gm/dl) anaemia in your daily practice?', 'type': 'radio', 'options': ['<50%','50-60%','60-70%','70-80%','>80%'] },
        { 'name': 'q2', 'title': 'What is the most common barrier to effective anaemia management in your practice?', 'type': 'radio', 'options': ['Patient non-compliance','Lack of diagnostic tools','Late antenatal registration','Limited access to IV iron'] },
        { 'name': 'q3', 'title': 'What is your first-line treatment for moderate anaemia (Hb 7–9.9 g/dL) in the second trimester?', 'type': 'radio', 'options': ['Oral iron therapy','Intravenous iron therapy','Blood transfusion','Dietary modification only'] },
        { 'name': 'q4', 'title': 'How effective do you find oral iron supplements in treating Moderate anaemia?', 'type': 'radio', 'options': ['Very effective','Effective','Moderately effective','Ineffective'] },
        { 'name': 'q5', 'title': 'How do you decide between oral and intravenous iron therapy for a Moderate Anaemic patient?', 'type': 'radio', 'options': ['Patient Economic stature','Patient Compliance','Patient Preference','Previous response to treatment'] },
        { 'name': 'q6', 'title': 'What is your preferred intravenous iron formulation for Moderate anaemia?', 'type': 'radio', 'options': ['Iron sucrose','Ferric carboxymaltose (FCM)','Iron dextran','Ferrous gluconate'] },
        { 'name': 'q7', 'title': 'How do you monitor the effectiveness of Moderate & Severe anaemia treatment? (Can mark more than 1, if necessary)', 'type': 'checkbox', 'options': ['Follow-up Hb levels','Patient-reported symptoms','Serum ferritin levels'] },
        { 'name': 'q8', 'title': 'How do you rate the safety profile of Ferric Carboxymaltose (FCM) in Moderate/Severe anaemia treatment?', 'type': 'radio', 'options': ['Excellent Safety','Good Safety','Moderately safe','Few Adverse Events Seen'] },
        { 'name': 'q9', 'title': 'What is the most significant advantage of using FCM over other treatments?', 'type': 'radio', 'options': ['Faster replenishment of iron stores','Assured Hb Rise','Fewer side effects','Single-dose administration','Better patient compliance'] },
        { 'name': 'q10', 'title': 'What is your primary indication for using 1000 mg FCM in pregnancy?', 'type': 'radio', 'options': ['Mild anaemia with Hb > 10 g/dL','Moderate anaemia with poor oral iron tolerance','Severe anaemia with low ferritin','Routine prophylaxis'] },
        { 'name': 'q11', 'title': 'Would you recommend 1000 mg FCM as a standard treatment for moderate to severe anaemia in pregnancy?', 'type': 'radio', 'options': ['Yes, strongly recommend','Yes, with some reservations','Only in selected cases','No, prefer other treatments'] },
        { 'name': 'q12', 'title': 'What is your biggest challenge in using 1000MG FCM in pregnancy?', 'type': 'radio', 'options': ['Cost','Availability','Patient acceptance','Institutional protocol restrictions','Risk of Adverse Events'] },
        { 'name': 'q13', 'title': 'What is your usual follow-up protocol after 1000MG FCM administration?', 'type': 'radio', 'options': ['No follow-up unless symptomatic','Hb and ferritin after 2–3 weeks','Hb only after 4 weeks','Clinical assessment at next ANC visit'] },
        { 'name': 'q14', 'title': 'What is your experience with patient tolerance to 1000 mg FCM infusion?', 'type': 'radio', 'options': ['Well tolerated, no issues','Mild side effects (headache, nausea)','Moderate reactions requiring observation','Avoid use due to past adverse events'] },
        { 'name': 'q15', 'title': 'What is the most common side effect you observe with intravenous iron therapy?', 'type': 'radio', 'options': ['Nausea','Rash','Hypotension','No significant side effects'] },
    ]

    # Load existing answers from session or init blank
    default_answers = {q['name']: ([] if q['type']=='checkbox' else '') for q in questions}
    answers = request.session.get('survey2_answers', default_answers)

    if request.method == 'POST':
        action = request.POST.get('submit_action', 'save')
        if action == 'reset':
            request.session['survey2_answers'] = default_answers
            messages.success(request, 'Selections cleared.')
            return redirect('survey2')

        # Gather answers
        new_answers = {}
        for q in questions:
            if q['type'] == 'checkbox':
                new_answers[q['name']] = request.POST.getlist(q['name'])
            else:
                new_answers[q['name']] = request.POST.get(q['name'], '')
        request.session['survey2_answers'] = new_answers
        request.session.modified = True

        if action == 'submit':
            messages.success(request, 'Survey submitted successfully!')
            request.session['last_survey_url'] = reverse('survey2')
            return redirect('survey_done')
        else:
            messages.success(request, 'Draft saved.')

    context = { 'questions': questions, 'answers': request.session.get('survey2_answers', answers) }
    return render(request, 'wtestapp/survey2.html', context)


@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def upload_survey_file(request):
    if request.method == 'POST':
        form = SurveyUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_name = uploaded_file.name

            try:
                with transaction.atomic():
                    created_surveys = []
                    portal = _get_portal_from_request(request)
                    if file_name.lower().endswith('.json'):
                        survey_data = json.loads(uploaded_file.read().decode('utf-8'))
                        if isinstance(survey_data, list):
                            for single_survey_data in survey_data:
                                print(f"--- Debug: Processing single JSON survey data ---")
                                print(f"  Data: {single_survey_data}")
                                s = _process_single_json_survey(single_survey_data)
                                if s:
                                    created_surveys.append(s)
                                print(f"----------------------------------------------------")
                        else:
                            print(f"--- Debug: Processing single JSON survey data ---")
                            print(f"  Data: {survey_data}")
                            s = _process_single_json_survey(survey_data)
                            if s:
                                created_surveys.append(s)
                            print(f"----------------------------------------------------")
                        messages.success(request, "JSON Survey(s) uploaded and processed successfully!")
                    elif file_name.lower().endswith(('.xls', '.xlsx')):
                        df = pd.read_excel(uploaded_file)
                        s = process_excel_survey(request, df)
                        if s:
                            created_surveys.append(s)
                        messages.success(request, "Excel Survey uploaded and processed successfully!")
                    else:
                        messages.error(request, "Unsupported file format. Please upload a JSON or Excel file.")
                        return render(request, 'wtestapp/upload_survey.html', {'form': form})

                    # Tag surveys with portal and auto-assign uploaded surveys to current doctor
                    try:
                        doctor, _ = Doctor.objects.get_or_create(user=request.user)
                        for s in created_surveys:
                            if portal and s.portal_type != portal:
                                s.portal_type = portal
                                s.save()
                            s.assigned_to.add(doctor)
                    except Exception as e:
                        print(f"Warn: could not auto-assign surveys to doctor: {e}")
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return render(request, 'wtestapp/upload_survey.html', {'form': form})

            # Redirect to My Surveys as requested
            return redirect('doctor_surveys_list')
    else:
        form = SurveyUploadForm()

    return render(request, 'wtestapp/upload_survey.html', {'form': form})

@login_required
def agreement_page(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    # Ensure each doctor has a fixed agreement amount; initialize if missing
    if not doctor.agreement_amount:
        doctor.agreement_amount = _next_agreement_amount()
        doctor.save(update_fields=["agreement_amount"])
    context = {
        'doctor': doctor,
        'amount': doctor.agreement_amount,
        'survey_title': 'Inclinic experience of Topical Sunscreen in Paediatric',
    }
    return render(request, 'wtestapp/agreement_page.html', context)

@login_required
def accept_agreement(request):
    if request.method == 'POST':
        if request.POST.get('agree') == 'on':
            doctor = get_object_or_404(Doctor, user=request.user)
            signature_data = request.POST.get('signature_data', '')
            signature_type = request.POST.get('signature_type', 'drawn')
            agreement_text = request.POST.get('agreement_text', '').strip()

            # Persist Agreement record
            Agreement.objects.update_or_create(
                doctor=doctor,
                defaults={
                    'agreement_text': agreement_text or 'I hereby agree to the terms and conditions.',
                    'digital_signature': signature_data if signature_data else None,
                    'signature_type': signature_type,
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                }
            )

            # Mark on Doctor for quick checks
            doctor.agreement_accepted = True
            doctor.save()
            messages.success(request, "Participant Agreement accepted.")
            # Redirect to assigned surveys list
            return redirect('doctor_surveys_list')
        else:
            messages.error(request, "You must accept the agreement to continue.")
    return redirect('agreement_page') # Redirect back to agreement page if not POST or agreement not checked

@login_required
def download_agreement_pdf(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    # Make sure the agreement has been accepted before allowing download
    if not doctor.agreement_accepted:
        messages.error(request, "You must accept the agreement before downloading the PDF.")
        return redirect('agreement_page')

    template_path = 'wtestapp/agreement_pdf_template.html'
    # Use per-doctor fixed agreement amount; rotate through the sequence if missing
    if not doctor.agreement_amount:
        doctor.agreement_amount = _next_agreement_amount()
        doctor.save(update_fields=["agreement_amount"])
    amount = doctor.agreement_amount

    context = {
        'doctor': doctor,
        'survey_title': 'Inclinic experience of Topical Sunscreen in Paediatric',
        'amount': amount,
    }
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="participant_agreement.pdf"'
    pisa_status = pisa.CreatePDF(
        html,                # the HTML to convert
        dest=response,       # file handle to receive result
        link_callback=link_callback) # Use the link_callback

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Helper to assign the next agreement amount in a rotating sequence
def _next_agreement_amount():
    amounts = [10000, 20000, 25000, 30000]
    # Count doctors that already have an amount to rotate fairly
    used_count = Doctor.objects.filter(agreement_amount__isnull=False).count()
    return amounts[used_count % len(amounts)]


@login_required
def admin_dashboard_view(request):
    """Simple admin dashboard filtered by portal type via ?portal=CP|GC.
    This is a lightweight custom view; you can also use Django Admin.
    """
    portal = request.GET.get('portal')

    doctors = Doctor.objects.all()
    surveys = Survey.objects.all()
    agreements = Agreement.objects.all()
    responses = SurveyResponse.objects.all()

    if portal in ('CP', 'GC'):
        doctors = doctors.filter(portal_type=portal)
        surveys = surveys.filter(portal_type=portal)
        agreements = agreements.filter(doctor__portal_type=portal)
        responses = responses.filter(survey__portal_type=portal)

    context = {
        'portal': portal,
        'doctors': doctors.select_related('user').order_by('-created_at'),
        'surveys': surveys.order_by('-created_at'),
        'agreements': agreements.select_related('doctor__user').order_by('-signed_at'),
        'responses': responses.select_related('doctor__user', 'survey').order_by('-started_at'),
    }
    return render(request, 'wtestapp/admin_dashboard.html', context)

@login_required
def doctor_status(request):
    """Return JSON with doctor's profile completeness and agreement status."""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        # If doctor not created yet, treat as incomplete and not agreed
        return JsonResponse({
            'exists': False,
            'profile_complete': False,
            'agreement_accepted': False,
        })

    profile_complete = all([
        doctor.first_name, doctor.last_name, doctor.email, doctor.mobile,
        doctor.address, doctor.specialty, doctor.mci_registration, doctor.pan
    ])
    return JsonResponse({
        'exists': True,
        'profile_complete': profile_complete,
        'agreement_accepted': bool(doctor.agreement_accepted),
    })

def _process_single_json_survey(survey_data):
    print(f"--- Debug: _process_single_json_survey called ---")
    print(f"Received survey_data: {survey_data}")
    # Title/description fallbacks
    survey_title = survey_data.get('title') or survey_data.get('survey_title') or survey_data.get('name')
    if not survey_title:
        raise ValueError("JSON survey data is missing the 'title' field.")
    survey_description = survey_data.get('description') or survey_data.get('desc') or ''

    # Deduplicate any existing surveys with same title
    existing = Survey.objects.filter(title=survey_title).order_by('id')
    if existing.exists():
        survey = existing.first()
        # Delete duplicates beyond the first (we'll recreate questions from JSON anyway)
        for dup in existing[1:]:
            dup.delete()
        # Update description if needed
        if survey.description != survey_description:
            survey.description = survey_description
            survey.save()
        created = False
    else:
        survey = Survey.objects.create(title=survey_title, description=survey_description)
        created = True
    print(f"Survey created/updated: {survey.title} (ID: {survey.id}, Created: {created})")

    # Identify questions list robustly
    questions_block = (
        survey_data.get('questions')
        or survey_data.get('Questions')
        or survey_data.get('items')
        or (survey_data if isinstance(survey_data, list) else [])
    )

    order_counter = 1
    for q_data in questions_block:
        question_text = q_data.get('question_text')
        if not question_text:
            # Common alt keys
            question_text = q_data.get('question') or q_data.get('text') or q_data.get('label')

        # Accept several aliases for type and normalize to our internal choices
        question_type_raw = q_data.get('question_type') or q_data.get('type') or q_data.get('input') or None
        qtype = str(question_type_raw).strip().lower()
        type_map = {
            'mcq': 'radio',
            'single': 'radio',
            'single_choice': 'radio',
            'multiple': 'checkbox',
            'multi': 'checkbox',
            'multi_select': 'checkbox',
            'yes/no': 'yesno',
            'yes_no': 'yesno',
            'yn': 'yesno',
            'longtext': 'textarea',
            'paragraph': 'textarea',
            'number': 'number',
            'email': 'email',
            'phone': 'phone',
            'rating': 'rating',
            'text': 'text',
            'textarea': 'textarea',
            'radio': 'radio',
            'checkbox': 'checkbox',
        }
        question_type = type_map.get(qtype, 'text') if qtype else 'text'
        raw_options = (
            q_data.get('options')
            or q_data.get('choices')
            or q_data.get('values')
            or q_data.get('data')
            or []
        )  # options may be list/str/dict

        # Normalize options into a simple list of strings
        options = []
        if isinstance(raw_options, list):
            options = raw_options
        elif isinstance(raw_options, str):
            # comma-separated
            options = [o.strip() for o in raw_options.split(',') if o.strip()]
        elif isinstance(raw_options, dict):
            # common patterns: {"questions": [...]}, {"options": [...]}
            if 'questions' in raw_options and isinstance(raw_options['questions'], list):
                options = raw_options['questions']
            elif 'options' in raw_options and isinstance(raw_options['options'], list):
                options = raw_options['options']
            else:
                # fallback: use values if strings, else keys
                vals = list(raw_options.values())
                if all(isinstance(v, str) for v in vals):
                    options = vals
                else:
                    options = list(raw_options.keys())

        # If type wasn't provided but options exist, default to single-choice radio
        if (not question_type_raw) and options:
            question_type = 'radio'

        if not question_text:
            print(f"Warning: Skipping question due to missing question_text in JSON data: {q_data}")
            continue

        q, q_created = Question.objects.update_or_create(
            survey=survey,
            question_text=question_text,
            defaults={'question_type': question_type, 'options': options, 'order': order_counter}
        )
        order_counter += 1
        print(f"  Question created/updated: {q.question_text} (ID: {q.id}, Type: {q.question_type}, Options: {q.options}, Created: {q_created})")
    print(f"--- Debug: _process_single_json_survey finished ---")
    return survey

def process_excel_survey(request, df):
    # Assuming the first row contains survey title and description
    # Example: df.iloc[0, 0] = "Clinical Insights of Physicians"
    # df.iloc[1, 0] = "To understand the effectiveness..."

    if df.empty or df.shape[1] < 2:
        raise ValueError("Excel file is empty or does not contain enough columns for survey title/description.")

    survey_title = df.iloc[0, 1]  # Assuming title is in B1 (0-indexed col 1)
    if pd.isna(survey_title) or str(survey_title).strip() == '':
        raise ValueError("Excel file is missing the survey title in cell B1.")
    survey_title = str(survey_title).strip()

    survey_description = df.iloc[1, 1]  # Assuming description is in B2 (0-indexed col 1)
    if pd.isna(survey_description):
        survey_description = ''
    else:
        survey_description = str(survey_description).strip()

    # Avoid MultipleObjectsReturned for same title
    survey = Survey.objects.filter(title=survey_title).first()
    created = False
    if survey:
        if survey.description != survey_description:
            survey.description = survey_description
            survey.save()
    else:
        survey = Survey.objects.create(title=survey_title, description=survey_description)
        created = True

    # Assuming questions start from row 5 (0-indexed row 4),
    # with columns: B: Question Text, C: Question Type, D: Options (comma-separated string)

    # Start iterating from index 4 (Excel row 5) to skip headers
    order_counter = 1
    for index, row in df.iloc[4:].iterrows(): 
        # Check if the row is entirely empty
        if row.isnull().all():
            continue # Skip empty rows gracefully
            
        # Access columns by index, providing defaults for robustness
        question_text_raw = row.iloc[1] if row.shape[0] > 1 else None # Column B
        question_type_raw = row.iloc[2] if row.shape[0] > 2 else None # Column C
        options_str_raw = row.iloc[3] if row.shape[0] > 3 else None   # Column D

        question_text = str(question_text_raw).strip() if not pd.isna(question_text_raw) else ''
        question_type = str(question_type_raw).strip() if not pd.isna(question_type_raw) else 'text'
        options_str = str(options_str_raw).strip() if not pd.isna(options_str_raw) else ''
        options = [o.strip() for o in options_str.split(',')] if options_str else []

        if not question_text:
            messages.warning(request, f"Skipping row {index + 1} in Excel: Question text is empty or missing.")
            continue

        # Normalize type aliases similar to JSON handler
        qtype = str(question_type).lower()
        type_map = {
            'mcq': 'radio', 'single': 'radio', 'single_choice': 'radio',
            'multiple': 'checkbox', 'multi': 'checkbox', 'multi_select': 'checkbox',
            'yes/no': 'yesno', 'yes_no': 'yesno', 'yn': 'yesno',
            'longtext': 'textarea', 'paragraph': 'textarea',
            'number': 'number', 'email': 'email', 'phone': 'phone', 'rating': 'rating',
            'text': 'text', 'textarea': 'textarea', 'radio': 'radio', 'checkbox': 'checkbox'
        }
        question_type = type_map.get(qtype, 'text')

        Question.objects.update_or_create(
            survey=survey,
            question_text=question_text,
            defaults={'question_type': question_type, 'options': options, 'order': order_counter}
        )
        order_counter += 1

    return survey
