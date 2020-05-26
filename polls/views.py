from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.db.models import F
from django.utils import timezone

from .models import Choice, Question

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published question 
        (excluding those which pub_date is in the future).
        """
        returnlist = []
        for question in Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date'):
            if question.choice_set.all():  # Ignore questions without choices
                returnlist.append(question)
            if returnlist == 5:
                break
        return returnlist     
#        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    queryset = Question.objects.filter(pub_date__lte=timezone.now())
    
    def get_queryset(self): # override queryset
        """
        Excludes any questions that aren't published yet.
        """
        question = get_object_or_404(Question, pk=self.kwargs.get("pk"))
        choices = question.choice_set.all()
        if choices:
            return Question.objects.filter(pub_date__lte=timezone.now())
        else: 
            # This should redirect to index
            raise Http404("Question is incomplete (has no choices)")
        #return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self): # override queryset
            """
            Excludes any questions that aren't published yet.
            """
            question = get_object_or_404(Question, pk=self.kwargs.get("pk"))
            choices = question.choice_set.all()
            if choices:
                return Question.objects.filter(pub_date__lte=timezone.now())
            else: 
                # This should redirect to index
                raise Http404("Question is incomplete (has no choices)")
            #return Question.objects.filter(pub_date__lte=timezone.now())

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try: 
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))    
    