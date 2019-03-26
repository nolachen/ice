from django import forms

from courses.models import Course, Question, Answer

import logging
logger = logging.getLogger(__name__)

"""
For adding new courses
"""
class CourseForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = ['name', 'description']

class QuizForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        self.questions = questions
        
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            choices = (
                ('A', 'choice 1'),
                ('B', 'choice 2'),
                ('C', 'choice 3'),
                ('D', 'choice 4'),
            )
            
            """
            for answer in Answer.objects.filter(question_id=question.question_id):
                choices.append(answer.answer_text)
            ## May need to pass some initial data, etc:
            """
            self.fields[question] = forms.ChoiceField(label=question, required=True, 
                                        choices=choices, widget=forms.RadioSelect)
    def save(self):
        pass