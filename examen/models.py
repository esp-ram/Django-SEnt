from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.utils import timezone
from datetime import date



class Exam(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField(default=date.today)
    start = models.DateTimeField()
    end = models.DateTimeField()
    exercises = models.PositiveIntegerField()
    report = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.titulo

    def __unicode__(self):
        return self.titulo

    def db_safe_title(self):
        return (self.titulo).replace(' ','')

    def is_active(self, current_date):
        return (self.end > current_date) and (self.start < current_date)

    class Meta:
        verbose_name_plural = "Exams"



class Professor(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    available = models.BooleanField(default=False)


    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    def db_safe_name(self):
        return (self.nombre).replace(' ','')

    class Meta:
        verbose_name_plural = "Professors"


class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.PositiveIntegerField()
    exam = models.ForeignKey(Exam, on_delete=CASCADE)
    ex_submitted = models.PositiveIntegerField()
    data_key = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre

    def __unicode__(self):
        return self.nombre

    def db_safe_name(self):
        return (self.nombre).replace(' ','')

    class Meta:
        verbose_name_plural = "Students"

        