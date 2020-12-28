from django.contrib import admin

# Register your models here.
from main.models import Profile, Notes, Tags

admin.site.register(Profile)
admin.site.register(Tags)


@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags',)
