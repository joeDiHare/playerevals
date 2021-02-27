from django.core.management.base import BaseCommand
import pandas as pd

from playerevals.models import *

POSITIONS = ["[2] Right/Left Wing-Back","[3] Centre Back","[4] Sweeper","[5] Defensive midfield","[6] Centre midfield","[7] Winger","[8] Wide midfield","[9] Second striker","[10] Attacking midfield","[11] Forward / Striker"]

class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):

        df_reviewers = pd.read_csv('playerevals/reviewers.csv')
        CODES = df_reviewers['code'].values
        PLAYERS = df_reviewers['players'].values
        REVIEWERS = df_reviewers['reviewer'].values

        for p in REVIEWERS:
            obj, created = Players.objects.get_or_create(name=p)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Player {p}'))
        
        for r, c, pp in zip(REVIEWERS, CODES, PLAYERS):
            obj, created = Reviewer.objects.get_or_create(
                name=r,
                code=c,
                assigned_players=pp,
                completed_reviews='')
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created Reviewer {r} with code {c} and players:{pp}'))

        df = pd.read_csv('playerevals/skills.csv')
        for k, row in df.iterrows():
            obj, created = Skills.objects.get_or_create(
                                slug=row['skill'].replace(' ', '_'),
                                name=row['skill'],
                                description=row['description'],
                                ref_value=row['ref'])
            if not created:
                continue
            obj.save()
            self.stdout.write(self.style.SUCCESS(f'Created Skill-Question {row["skill"]}'))
        
        # for r in RATINGS:
        #     obj, created = Skills.objects.get_or_create(name=s)
        #     if created:
        #         self.stdout.write(self.style.SUCCESS(f'Created rating {r}'))

        

