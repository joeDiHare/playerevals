from collections import Counter
import json
import pandas as pd

from django.core import serializers
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse

from .models import *


class EvalView(generic.ListView):
    model = Skills
    template_name = 'playerevals/eval.html'

    def get(self, *args, **kwargs):

        if self.kwargs['rid'] == 'download':
            return download()
        
        rev = Reviewer.objects.filter(code=self.kwargs['rid'])
        if not rev:
            return HttpResponseRedirect(reverse('playerevals:lost'))

        rev = rev.first()
        if len(rev.remaining()) == 0:
            return HttpResponseRedirect(
                reverse('playerevals:done', args=(rev.name,)))

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rid = self.kwargs['rid']
        rev = Reviewer.objects.get(code=rid)

        context['reviewer'] = rev
        context['status'] = [(p[0], p in rev.completed_reviews)
                             for p in rev.assigned_players.split('|')]
        context['next_player'] = rev.next_player()
        context['rem'] = len(rev.remaining())
        context['questions'] = Skills.objects.all()
        context['skills'] = Skills.objects.all()
        context['players'] = Players.objects.all()
        context['rid_str'] = rid
        return context


class PlayerView(generic.ListView):
    model = Review
    template_name = 'playerevals/player.html'

    def get(self, *args, **kwargs):
        
        rev = Reviewer.objects.filter(code=self.kwargs['rid'])
        if not rev:
            return HttpResponseRedirect(reverse('playerevals:lost'))
        return super().get(*args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rid = self.kwargs['rid']
        reviewer_obj = Reviewer.objects.get(code=rid)
        player_obj = Players.objects.get(name=reviewer_obj.name)
        reviews = Review.objects.filter(player=player_obj)
        df_skl = pd.DataFrame([json.loads(r.data)['skills'] for r in reviews])
        df_all_skl = pd.DataFrame([json.loads(r.data)['skills'] for r in Review.objects.all()])

        P = set()
        for r in reviews:
            for p, val in json.loads(r.data)['positions'].items():
                if val:
                    P.add(p)
        context['positions'] = list(P)

        C = Counter()
        for r in reviews:
            for n, val in json.loads(r.data)['awards'].items():
                if val:
                    C[NOMINATIONS[n]] += 1
        context['nominations'] = C.most_common()

        context['skills'] = [(
            s.name,
            s.description,
            int(20 * df_skl[f'{s.slug}'].astype(int).mean()),
            int(20 * df_all_skl[f'{s.slug}'].astype(int).mean()),
            int(20 * df_all_skl[f'{s.slug}'].astype(int).std()))
                for s in Skills.objects.all()]

        context['player'] = player_obj.name
        context['feedback'] = [json.loads(r.data)['feedback'].strip() for r in reviews]
        context['rid_str'] = rid
        return context


def vote(request, rid):
    player_name = request.POST[f"next_player"]
    rev = Reviewer.objects.get(code=rid)
    ply = Players.objects.get(name=player_name)

    skills = {}
    for s in Skills.objects.all():
        _key = f"c{s.slug.replace(' ', '_')}"
        choice = request.POST.get(_key, 3)
        skills.update({s.slug: choice})
    positions = {}
    for p in range(2, 12):
        positions.update({f"p{p}": request.POST.get(f"p{p}")})
    awards = {}
    for n in range(1, 8):
        awards.update({f"n{n}": request.POST.get(f"n{n}")})
    feedback = request.POST.get(f"feedback", "")

    # Save Review data
    data = {
        'reviewer': rev.name,
        'rid': rev.code,
        'player': player_name,
        'skills': skills,
        'positions': positions,
        'awards': awards,
        'feedback': feedback,
    }
    Review(data=json.dumps(data),
           reviewer=rev,
           player=ply).save()

    # Update Reviewer Status
    rev.add_review(player_name)
    rev.save()

    # Write local, as backup
    with open(f"{rev.code}_{ply.name}_review.json", 'w') as outfile:
        json.dump(data, outfile)

    return HttpResponseRedirect(reverse('playerevals:thanks', args=(rid,)))


class ThanksView(generic.TemplateView):
    template_name='playerevals/thanks.html'
    def get_context_data(self, **kwargs):
        rev = Reviewer.objects.get(code=self.kwargs['rid'])
        context = super().get_context_data(**kwargs)
        context['N'] = len(rev.remaining())
        return context

class DoneView(generic.ListView):
    model = Reviewer
    template_name = 'playerevals/done.html'

    def get_context_data(self, **kwargs):
        rev = Reviewer.objects.get(name=self.kwargs['reviewer'])
        context = super().get_context_data(**kwargs)
        context['N'] = len(rev.assigned_players.split('|'))
        context['reviewer'] = self.kwargs['reviewer']
        return context

class StartView(generic.TemplateView):
    template_name='playerevals/start.html'
    def get_context_data(self, **kwargs):
        rev = Reviewer.objects.get(code=self.kwargs['rid'])
        context = super().get_context_data(**kwargs)
        context['name'] = rev.name
        context['N'] = len(rev.remaining())
        return context

class LostView(generic.TemplateView):
    template_name='playerevals/lost.html'


class IndexView(generic.ListView):
    model = Reviewer
    template_name = 'playerevals/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = {}
        for rev in Reviewer.objects.all():
            _tmp = []
            for p in rev.assigned_players.split('|'):
                _tmp.append(p in rev.completed_reviews)
            context['status'][rev.name] = _tmp
        return context

def download():
    '''Flush Review model into json HttpResponse'''
    reviews = Review.objects.all()
    d = {}
    for k, rev in enumerate(reviews):
        d[k] = rev.data
    json_str = json.dumps(d)

    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'

    return response
