from django.core.management.base import BaseCommand
from wtestapp.models import Survey, Question

class Command(BaseCommand):
    help = 'Creates the default Clinical Insights of Physicians survey'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default survey and questions...'))

        survey_title = "Clinical Insights of Physicians"
        survey_description = "To understand the effectiveness of Natural ingredients including Shatavari in case of low breastmilk supply for new mothers"

        survey, created = Survey.objects.get_or_create(
            title=survey_title,
            defaults={'description': survey_description}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created survey: {survey.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'Survey \'{survey.title}\' already exists. Updating questions if necessary.'))

        questions_data = [
            {
                'question_text': "How frequently do you prescribe or recommend galactagogues to your breastfeeding patients?",
                'question_type': 'radio',
                'choices': "Rarely/Never, Occasionally (1-2 patients per month), Frequently (3-5 patients per month), Very Frequently (More than 5 patients per month)"
            },
            {
                'question_text': "For which of the following situations do you most commonly consider galactagogues? (Select all that apply)",
                'question_type': 'checkbox',
                'choices': "Perceived insufficient milk supply (PIMS), Preterm infants, Mothers returning to work, Mothers adopting infants, Induced lactation"
            },
            {
                'question_text': "What is your typical first-line approach for managing perceived insufficient milk supply?",
                'question_type': 'radio',
                'choices': "Reassurance and education on breastfeeding techniques, Frequent breastfeeding/pumping, Galactagogues, Referral to a lactation consultant"
            },
            {
                'question_text': "Which galactagogues do you commonly recommend or prescribe?",
                'question_type': 'checkbox',
                'choices': "Domperidone, Metoclopramide, Herbal supplements"
            },
            {
                'question_text': "What factors influence your decision to recommend or prescribe a galactagogue?",
                'question_type': 'checkbox',
                'choices': "Underlying cause of insufficient milk supply, Infant's age and health, Maternal health and medications, Patient preference, Availability and cost of galactagogue"
            },
            {
                'question_text': "How comfortable are you with prescribing or recommending galactagogues?",
                'question_type': 'radio',
                'choices': "Not at all comfortable, Somewhat comfortable, Comfortable, Very comfortable"
            },
            {
                'question_text': "What is your understanding of the evidence supporting the efficacy of galactagogues?",
                'question_type': 'radio',
                'choices': "Limited evidence, mainly anecdotal, Moderate evidence for some galactagogues, Strong evidence for most galactagogues, No evidence of benefit"
            },
            {
                'question_text': "Have you used Shatavari in your patients with lactation insufficiency?",
                'question_type': 'radio',
                'choices': "Yes, No"
            },
            {
                'question_text': "How would you rate efficacy of Shatavari as a galactagogue?",
                'question_type': 'radio',
                'choices': "Good, Very Good, Excellent"
            },
            {
                'question_text': "How do you typically monitor the effectiveness of galactagogues in your patients? (Select all that apply)",
                'question_type': 'checkbox',
                'choices': "Infant weight gain, Frequency of breastfeeding/pumping, Maternal reports of milk supply, Test weighing"
            },
        ]

        for q_data in questions_data:
            question, created = Question.objects.update_or_create(
                survey=survey,
                question_text=q_data['question_text'],
                defaults={
                    'question_type': q_data['question_type'],
                    'choices': q_data['choices']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added question: {question.question_text[:50]}...'))
            else:
                self.stdout.write(self.style.WARNING(f'Updated question: {question.question_text[:50]}...'))

        self.stdout.write(self.style.SUCCESS('Default survey and questions creation complete.'))
