import json

from django.core import serializers
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import *


class DetailView(generic.ListView):
    model = Skills
    template_name = 'playerevals/detail.html'

    def get(self, *args, **kwargs):

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


def vote(request, rid):
    print('here')
    player_name = request.POST[f"next_player"]
    rev = Reviewer.objects.get(code=rid)
    ply = Players.objects.get(name=player_name)

    skills = {}
    for s in Skills.objects.all():
        _key = f"c{s.slug.replace(' ', '_')}"
        choice = request.POST.get(_key, 3)
        skills.update({s.slug: choice})
        print(s.slug, choice)
    positions = {}
    for p in range(2, 12):
        positions.update({f"p{p}": request.POST.get(f"p{p}")})
    awards = {}
    for n in range(1, 8):
        awards.update({f"n{p}": request.POST.get(f"n{n}")})
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
    r = Review(data=json.dumps(data),
               reviewer=rev,
               player=ply)
    r.save()

    # Update Reviewer Status
    rev.add_review(player_name)
    rev.save()

    # Write local, as backup
    with open(f"{rev.code}_{rev.name}.csv", 'w') as outfile:
        json.dump(data, outfile)

    return HttpResponseRedirect(reverse('playerevals:detail', args=(rid,)))


class DoneView(generic.ListView):
    model = Reviewer
    template_name = 'playerevals/done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rev = Reviewer.objects.get(name=self.kwargs['reviewer'])
        context['tot'] = len(rev.assigned_players)
        context['reviewer'] = self.kwargs['reviewer']
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


def dumpdb(request):
    # Flush Review model into json HttpResponse
    reviews = Review.objects.all()
    d = {}
    for k, rev in enumerate(reviews):
        d[k] = rev.data
    json_str = json.dumps(d)

    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'

    return response
