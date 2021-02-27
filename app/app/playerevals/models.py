from django.db import models
from django.utils import timezone
import datetime
  

class Players(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.id}: {self.name}"

class Reviewer(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)
    assigned_players = models.TextField(null=True)
    completed_reviews = models.TextField(null=True)
    def remaining(self):
        assigned_players = self.assigned_players.split('|')
        completed_reviews = self.completed_reviews.split('|')
        rem = list(set(assigned_players) - set(completed_reviews))
        return rem
    def next_player(self):
        for p in self.assigned_players.split('|'):
            if p not in self.completed_reviews:
                return p
        return None
    def add_review(self, player):
        cr = self.completed_reviews.split('|')
        cr += [player]
        self.completed_reviews = '|'.join(cr)
    def __str__(self):
        return f"{self.id}: {self.name}"

class Skills(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    # value = models.IntegerField(default=3)
    ref_value = models.FloatField(default=0.0)
    def __str__(self):
        return f"{self.id}: {self.name}"

class Review(models.Model):
    ts = models.DateTimeField(auto_now_add=True)
    data = models.CharField(max_length=1000)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    player = models.ForeignKey(Players, on_delete=models.CASCADE)
