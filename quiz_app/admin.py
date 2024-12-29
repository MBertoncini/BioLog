from django.contrib import admin
from .models import Species, Region, Month, Question, Achievement, UserAchievement

admin.site.register(Species)
admin.site.register(Region)
admin.site.register(Month)
admin.site.register(Question)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'condition')

admin.site.register(Achievement, AchievementAdmin)
admin.site.register(UserAchievement)