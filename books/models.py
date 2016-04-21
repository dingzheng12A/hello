#coding=utf-8
from django.db import models
from django.contrib import admin
class NewsAdmin(admin.ModelAdmin):


	class Media:
		js=('/js/tinymce/tinymce.min.js','/js/textareas.js')


class book(models.Model):
	name=models.CharField(max_length=50)
	author=models.CharField(max_length=20)
	price=models.FloatField()
	importdate=models.DateTimeField()
	user=models.CharField(max_length=20)
	


#admin.site.register(NewsAdmin)
# Create your models here.
