#coding=utf-8
from django import forms
from tinymce.widgets import TinyMCE
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from haha.books.models import book
import time


class RegForm(forms.Form):
	Username=forms.CharField(max_length=50,label='用户名')
	email=forms.EmailField(required=False,label='个人邮箱')
	Password=forms.CharField(max_length=100,label='密  码',widget=forms.PasswordInput)
	Password1=forms.CharField(max_length=100,label='确认密码',widget=forms.PasswordInput)
	


	def clean_Username(self):
		Username=self.cleaned_data['Username']
		if len(Username)<5:
			raise forms.ValidationError('用户名不能少于5个字符')
		user=User.objects.filter(username=Username)
		if len(user)>0:
			raise forms.ValidationError('用户名已经存在!')
		return Username
	def clean_email(self):
		email=self.cleaned_data['email']
		user=User.objects.filter(email=email)
		if len(user)>0:
			raise forms.ValidationError('该邮箱地址已经注册！')
		return email

	def clean_Password(self):
		Password=self.cleaned_data['Password']
		if len(Password)<10:
			raise forms.ValidationError('密码不能少于10位!')
		have_alpha=False
		have_digit=False
		for i in Password:
			if i.isalpha():
				have_alpha=True
			if i.isdigit():
				have_digit=True
			
		if  have_alpha and have_digit:
			pass
		else:
			raise forms.ValidationError("密码必须包含有字母和数字！")
		return Password
	
	def clean_Password1(self):
		Password=self.cleaned_data.get('Password')
		Password1=self.cleaned_data['Password1']
		
		if Password!=Password1:
			raise forms.ValidationError("两次输入的密码不一致！")
		return Password,Password1



class PassForm(forms.Form):
	orignPass=forms.CharField(max_length=100,label='原始密码',widget=forms.PasswordInput)
	NewPass=forms.CharField(max_length=100,label='输入新密码',widget=forms.PasswordInput)
	ReptPass=forms.CharField(max_length=100,label="确认新密码",widget=forms.PasswordInput)

	def clean_NewPass(self):
		password=self.cleaned_data.get('NewPass')
		if len(password)<10:
			raise forms.ValidationError('密码不能少于10位!')
		have_alpha=False
		have_digit=False
		for i in password:
			if i.isalpha():
				have_alpha=True
			if i.isdigit():
				have_digit=True
			
		if  have_alpha and have_digit:
			pass
		else:
			raise forms.ValidationError("密码必须包含有字母和数字！")
		return password
	def clean_ReptPass(self):
		newpass=self.cleaned_data.get('NewPass')
		reptpass=self.cleaned_data.get('ReptPass')
		if  reptpass != newpass:
			raise forms.ValidationError("两次输入的密码不匹配！")
		return newpass,reptpass

class FlatPageForm(forms.Form):
	content=forms.CharField(widget=TinyMCE(attrs={'cols':80,'rows':30}))



class AddBook(forms.Form):
	bookname=forms.CharField(max_length=50,label="图书名称")
	author=forms.CharField(max_length=20,label="作者")
	price=forms.FloatField(label="价格(元)")


	def clean_bookname(self):
		bookname=self.cleaned_data['bookname']
		if(len(bookname)<3):
			raise forms.ValidationError("图书名不能小于三个字!")
		Book=book.objects.filter(name=bookname)
		if len(Book)>0:
			raise forms.ValidationError("该图书已经录入!")
		return bookname


class uploadform(forms.Form):
	files=forms.FileField(label='导入文件')	
