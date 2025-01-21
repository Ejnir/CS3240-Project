from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CommonUser, Project, ProjectMembership, ProjectFile, ProjectMessage

class CommonUserAdmin(UserAdmin):
    model = CommonUser
    list_display = ['email', 'username', 'real_name', 'is_admin', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin', 'real_name', 'date_joined_pma', 'interests')}),
    )

admin.site.register(CommonUser, CommonUserAdmin)
admin.site.register(Project)
admin.site.register(ProjectMembership)
admin.site.register(ProjectFile)
admin.site.register(ProjectMessage)
