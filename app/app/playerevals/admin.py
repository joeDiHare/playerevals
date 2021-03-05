from django.contrib import admin
from .models import *


class ReviewAdmin(admin.ModelAdmin):
    list_filter = ['reviewer']
    list_filter = ['player']
    search_fields = ['reviewer']

admin.site.register(Review, ReviewAdmin)

admin.site.register(Players)
admin.site.register(Reviewer)
admin.site.register(Skills)
