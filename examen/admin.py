from django.contrib import admin
from .models import Exam, Professor, Student
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group

admin.site.unregister(Group)

class ExamAdmin(admin.ModelAdmin):
    fields = ('title','date','start','end','exercises')
    search_fields = ['title']
    list_display = ('title', 'start', 'end', 'finished', 'submits', 'exercises', 'assign_professors')

    def submits(self,obj):
        return len(Student.objects.filter(exam_id = obj))

    def finished(self,obj):
        return obj.end <  timezone.now()

    def assign_professors(self, obj):
        if obj.report == 'N/A' :
            if self.finished(obj) :
                return format_html(
                 '<a  href="{0}" >Assign Professors</a>&nbsp;',
                 reverse('examen:assignation', kwargs={'exam_id' : obj.id} )
                )
            else:
                return format_html(
                 'The exam is not finished'
                )

        return format_html(
             '<a  href="{0}" >See Report</a>&nbsp;',
             reverse('examen:report', kwargs={'exam_id' : obj.id} )
        )

    assign_professors.short_description = 'Assign professor / See report'
    assign_professors.allow_tags = True


    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(Exam, ExamAdmin)


def available_false(modeladmin, request, queryset):
    queryset.update(available = False)

available_false.short_description = "Set selected as UNAVAILABLE"


def available_true(modeladmin, request, queryset):
    queryset.update(available = True)

available_true.short_description = "Set selected as AVAILABLE"



class ProfessorAdmin(admin.ModelAdmin):
    fields = ('name','email')
    list_display = ('name', 'email', 'available')
    actions = [available_false,available_true]
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Professor, ProfessorAdmin)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'exam', 'ex_submitted', 'data_key')
    list_filter = ('exam',)
    search_fields = ("student_id__startswith", )
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Student, StudentAdmin)