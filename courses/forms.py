from django import forms

from courses.models import Course

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
        for question in questions:
            field_name = "question_%d" % question.pk
            choices = ['test']
            #for answer in question.answer_set().all():
            #    choices.append((answer.pk, answer.answer_text,))
            ## May need to pass some initial data, etc:
            field = forms.ChoiceField(label=question.question_text, required=True, 
                                        choices=choices, widget=forms.RadioSelect)
        return super(QuizForm, self).__init__(*args, **kwargs)
    def save(self):
        pass