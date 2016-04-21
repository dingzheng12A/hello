#coding=utf-8
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from haha.forms import RegForm,PassForm,FlatPageForm,AddBook
from DjangoVerifyCode import Code
from haha.books.models import book
from django.utils.encoding import smart_str
import MySQLdb
import json
import time
import sys
import xlwt
import xlrd
import re
from xlrd import xldate_as_tuple
from haha.forms import uploadform
reload(sys)
sys.setdefaultencoding('utf-8')

def code(request):
	code=Code(request)
	return code.display()

def login(request):
	if request.method=='POST' and "captcha" not in request.REQUEST:
		username=request.POST['username']
		password=request.POST['password']
		user=authenticate(username=username,password=password)
		if user is not None and user.is_active:
			auth.login(request,user)
			request.session['username']=username
			return HttpResponseRedirect('/accounts/profile/')
		else:
			errors="have error"
			return render_to_response('registration/login.html',{'errors':errors})
	if request.method=='POST' and request.POST['captcha']:
		_code=request.POST.get('captcha')
		code=Code(request)
		if code.check(_code):
			username=request.POST['username']
                	password=request.POST['password']
			user=authenticate(username=username,password=password)
			if user is not None and user.is_active:
                        	auth.login(request,user)
                        	request.session['username']=username
                      	  	return HttpResponseRedirect('/accounts/profile/')
			else:
				errors="have error"
				return render_to_response("registration/login.html",{'errors':errors})
		else:
			capterr="验证码错误!"
			return render_to_response("registration/login.html",{'capterr':capterr,"code":code},context_instance=RequestContext(request))
	return render_to_response('registration/login.html')

def logout(request):
	auth.logout(request)
	return render_to_response('registration/logged_out.html')

@login_required(login_url='/accounts/')
def profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect("/accounts/")
	return render_to_response('registration/user.html',context_instance=RequestContext(request))

def reg(request):
	if request.method=='POST':
		form=RegForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data['Username']
			email=form.cleaned_data['email']
			password=form.cleaned_data['Password']
			user=User.objects.create(username=username,email=email)
			user.set_password(password)
			user.save()
			return HttpResponse("用户注册成功！请<a href='/accounts/'>登录</a>")
		
	else:
		form=RegForm()
	return render_to_response('registration/reg.html',{'form':form})


@login_required(login_url="/accounts/")
def password(request):
	username=request.GET['username']
	if request.method=='POST':
		form=PassForm(request.POST)
		if form.is_valid():
			password=form.cleaned_data['orignPass']
			newpass=form.cleaned_data.get('NewPass')
			user=authenticate(username=username,password=password)
			if user is None:
				error="用户密码不正确!"
				code="/code"
				return render_to_response('registration/pass.html',{'form':form,'error':error,'code':code})
			else:
				user.set_password(newpass)
				user.save()	
				message='更改密码成功!请重新登录!'
				return render_to_response('registration/pass.html',{'form':form,'message':message})
	else:
		form=PassForm()
	return render_to_response('registration/pass.html',{'form':form})		



@login_required
def addbook(request):
	if request.method=='POST':
		form=AddBook(request.POST)
		if form.is_valid():
			bookname=form.cleaned_data['bookname']
			author=form.cleaned_data['author']
			price=form.cleaned_data['price']
			importdate=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
			user=request.user
			Book=book.objects.create(name=bookname,author=author,price=price,importdate=importdate,user=user)
			Book.save()
			message="增加图书成功！"
			return render_to_response("registration/addbook.html",{'form':form,'message':message})
	else:
		form=AddBook()
	return render_to_response('registration/addbook.html',{'form':form})




@login_required
def booklist(request):
	if request.method=='POST':
		bookname=request.POST.get('bookname')
		author=request.POST.get('author')
		if len(bookname)>0:
			return render_to_response('registration/booklist.html',{'bookname':bookname})
		if len(author)>0:
			return render_to_response('registration/booklist.html',{'author':author})
	return render_to_response('registration/booklist.html')


@login_required
def test(request):
	page=request.GET.get('page')
	int_page=int(page)
	pages=int_page*3
	if 'bookname' in request.GET:
		bookname=request.GET.get('bookname')
		conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
		cursor=conn.cursor()
		if 'order' in request.GET:
			order=request.GET.get('order')
			if int(order)==1:
				sql="select name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' order by price  limit "+str(pages)+",3;"
			else:
				sql="select name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' order by price desc limit "+str(pages)+",3;"
		else:
			sql="select name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' limit "+str(pages)+",3;"
		sql1="select name,author,price,importdate from books_book where name like '%"+str(bookname)+"%';"
		cursor.execute("set names utf8;")
		cursor.execute(sql)
		infors=cursor.fetchall()
		ress=[]
		for infor in infors:
			ress.append({'bookname':infor[0],'author':infor[1],'price':infor[2],'importdate':infor[3]})
		count=cursor.execute(sql1)
		if count%3==0:
			number_pages=count/3
		else:
			number_pages=count/3+1
		end_pages=number_pages-1
		if int_page==0:
			has_priv=False
		else:
			has_priv=True
		if int_page==end_pages:
			has_next=False
		else:
			has_next=True	
		next_page=int_page+1
		priv_page=int_page-1
		cursor.close()
		conn.close()
		if 'order' in request.GET:
			return render_to_response('registration/test.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'order':request.GET.get('order')})
		return render_to_response('registration/test.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname})
	if 'author' in request.GET:
		author=request.GET.get('author')
		conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
		cursor=conn.cursor()
		if 'order' in request.GET:
			order=request.GET.get('order')
			if int(order)==1:
				sql="select name,author,price,importdate from books_book where author like '%"+str(author)+"%' order by price limit "+str(pages)+",3;"
			else:
				sql="select name,author,price,importdate from books_book where author like '%"+str(author)+"%' order by price desc limit "+str(pages)+",3;"
		else:
			sql="select name,author,price,importdate from books_book where author like '%"+str(author)+"%' limit "+str(pages)+",3;"
		sql1="select name,author,price,importdate from books_book where author like '%"+str(author)+"%';"
		cursor.execute("set names utf8;")
		cursor.execute(sql)
		infors=cursor.fetchall()
		ress=[]
		for infor in infors:
			ress.append({'bookname':infor[0],'author':infor[1],'price':infor[2],'importdate':infor[3]})
		count=cursor.execute(sql1)
		if count%3==0:
			number_pages=count/3
		else:
			number_pages=count/3+1
		end_pages=number_pages-1
		if int_page==0:
			has_priv=False
		else:
			has_priv=True
		if int_page==end_pages:
			has_next=False
		else:
			has_next=True	
		next_page=int_page+1
		priv_page=int_page-1
		cursor.close()
		conn.close()
		if 'order' in request.GET:
			return render_to_response('registration/test.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'author':author,'order':order})
		return render_to_response('registration/test.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'author':author})
	return render_to_response('registration/test.html',{'ress':ress,'bookname':bookname})



@login_required
def modifybook(request):
	if request.method=='POST':
		bookname=request.POST.get('bookname')
		author=request.POST.get('author')
		return render_to_response('registration/modifybook.html',{'bookname':bookname,'author':author})
	return render_to_response('registration/modifybook.html')	



@login_required
def modify(request):
	page=request.GET.get('page')
	int_page=int(page)
	pages=int_page*3
	if 'bookname' in request.GET and 'author' in request.GET: 
		bookname=request.GET.get('bookname')
		author=request.GET.get('author')
		conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
		cursor=conn.cursor()
		if 'order' in request.GET:
			order=request.GET.get('order')
			if int(order)==1:
				sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%' order by price  limit "+str(pages)+",3;"
			else:
				sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%' order by price desc limit "+str(pages)+",3;"
		else:
			sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%' limit "+str(pages)+",3;"
		sql1="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%';"
		cursor.execute("set names utf8;")
		cursor.execute(sql)
		infors=cursor.fetchall()
		ress=[]
		for infor in infors:
			ress.append({'id':infor[0],'bookname':infor[1],'author':infor[2],'price':infor[3],'importdate':infor[4]})
		count=cursor.execute(sql1)
		if count%3==0:
			number_pages=count/3
		else:
			number_pages=count/3+1
		end_pages=number_pages-1
		if int_page==0:
			has_priv=False
		else:
			has_priv=True
		if int_page==end_pages:
			has_next=False
		else:
			has_next=True	
		next_page=int_page+1
		priv_page=int_page-1
		cursor.close()
		conn.close()
		if 'order' in request.GET:
			return render_to_response('registration/modify.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'author':author,'order':request.GET.get('order')})
		return render_to_response('registration/modify.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'author':author})
	else:
		if 'author' in request.GET:
			author=request.GET.get('author')
			conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
			cursor=conn.cursor()
			if 'order' in request.GET:
				order=request.GET.get('order')
				if int(order)==1:
					sql="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%' order by price limit "+str(pages)+",3;"
				else:
					sql="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%' order by price desc limit "+str(pages)+",3;"
			else:
				sql="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%' limit "+str(pages)+",3;"
			sql1="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%';"
			cursor.execute("set names utf8;")
			cursor.execute(sql)
			infors=cursor.fetchall()
			ress=[]
			for infor in infors:
				ress.append({'id':infor[0],'bookname':infor[1],'author':infor[2],'price':infor[3],'importdate':infor[4]})
			count=cursor.execute(sql1)
			if count%3==0:
				number_pages=count/3
			else:
				number_pages=count/3+1
			end_pages=number_pages-1
			if int_page==0:
				has_priv=False
			else:
				has_priv=True
			if int_page==end_pages:
				has_next=False
			else:
				has_next=True	
			next_page=int_page+1
			priv_page=int_page-1
			cursor.close()
			conn.close()
			if 'order' in request.GET:
				return render_to_response('registration/modify.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'author':author,'order':order})
			return render_to_response('registration/modify.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'author':author})
		else:
			if 'bookname' in request.GET:
				bookname=request.GET.get('bookname')
				conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
				cursor=conn.cursor()
				if 'order' in request.GET:
					order=request.GET.get('order')
					if int(order)==1:
						sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' order by price limit "+str(pages)+",3;"
					else:
						sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' order by price desc limit "+str(pages)+",3;"
				else:
					sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' limit "+str(pages)+",3;"
				sql1="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%';"
				cursor.execute("set names utf8;")
				cursor.execute(sql)
				infors=cursor.fetchall()
				ress=[]
				for infor in infors:
					ress.append({'id':infor[0],'bookname':infor[1],'author':infor[2],'price':infor[3],'importdate':infor[4]})
				count=cursor.execute(sql1)
				if count%3==0:
					number_pages=count/3
				else:
					number_pages=count/3+1
				end_pages=number_pages-1
				if int_page==0:
					has_priv=False
				else:
					has_priv=True
				if int_page==end_pages:
					has_next=False
				else:
					has_next=True	
				next_page=int_page+1
				priv_page=int_page-1
				cursor.close()
				conn.close()
				if 'order' in request.GET:
					return render_to_response('registration/modify.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'order':order})
				return render_to_response('registration/modify.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname})
		return render_to_response('registration/modify.html',{'ress':ress,'bookname':bookname})






@login_required
def update(request):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	if request.method=='POST':
		id=request.POST.get('id').strip()
		bookname=request.POST.get('bookname')
		author=request.POST.get('author')
		price=request.POST.get('price')
		conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha',charset='utf8')
		sql="update books_book set name='%s',author='%s',price=%f where id=%d" %(bookname,author,float(price),int(id))
		cursor=conn.cursor()
		cursor.execute("set names utf8")
		cursor.execute(sql)
		conn.commit()
		cursor.close()
		conn.close()
	return HttpResponse("")	


@login_required
def deletebook(request):
	if request.method=='POST':
		bookname=request.POST.get('bookname')
		author=request.POST.get('author')
		return render_to_response('registration/deletebook.html',{'bookname':bookname,'author':author})
	return render_to_response('registration/deletebook.html')	

@login_required
def delete(request):
	page=request.GET.get('page')
	int_page=int(page)
	pages=int_page*3
	if 'bookname' in request.GET and 'author' in request.GET: 
		bookname=request.GET.get('bookname')
		author=request.GET.get('author')
		conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
		cursor=conn.cursor()
		if 'order' in request.GET:
			order=request.GET.get('order')
			if int(order)==1:
				sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%' order by price  limit "+str(pages)+",3;"
		else:
			sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%' limit "+str(pages)+",3;"
		sql1="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' and author like '%"+str(author)+"%';"
		cursor.execute("set names utf8;")
		cursor.execute(sql)
		infors=cursor.fetchall()
		ress=[]
		for infor in infors:
			ress.append({'id':infor[0],'bookname':infor[1],'author':infor[2],'price':infor[3],'importdate':infor[4]})
		count=cursor.execute(sql1)
		if count%3==0:
			number_pages=count/3
		else:
			number_pages=count/3+1
		end_pages=number_pages-1
		if int_page==0:
			has_priv=False
		else:
			has_priv=True
		if int_page==end_pages:
			has_next=False
		else:
			has_next=True	
		next_page=int_page+1
		priv_page=int_page-1
		cursor.close()
		conn.close()
		if 'order' in request.GET:
			return render_to_response('registration/delete.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'author':author,'order':request.GET.get('order')})
		return render_to_response('registration/delete.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'author':author})
	else:
		if 'author' in request.GET:
			author=request.GET.get('author')
			conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
			cursor=conn.cursor()
			if 'order' in request.GET:
				order=request.GET.get('order')
				if int(order)==1:
					sql="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%' order by price limit "+str(pages)+",3;"
				else:
					sql="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%' order by price desc limit "+str(pages)+",3;"
			else:
				sql="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%' limit "+str(pages)+",3;"
			sql1="select id,name,author,price,importdate from books_book where author like '%"+str(author)+"%';"
			cursor.execute("set names utf8;")
			cursor.execute(sql)
			infors=cursor.fetchall()
			ress=[]
			for infor in infors:
				ress.append({'id':infor[0],'bookname':infor[1],'author':infor[2],'price':infor[3],'importdate':infor[4]})
			count=cursor.execute(sql1)
			if count%3==0:
				number_pages=count/3
			else:
				number_pages=count/3+1
			end_pages=number_pages-1
			if int_page==0:
				has_priv=False
			else:
				has_priv=True
			if int_page==end_pages:
				has_next=False
			else:
				has_next=True	
			next_page=int_page+1
			priv_page=int_page-1
			cursor.close()
			conn.close()
			if 'order' in request.GET:
				return render_to_response('registration/delete.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'author':author,'order':order})
			return render_to_response('registration/delete.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'author':author})
		else:
			if 'bookname' in request.GET:
				bookname=request.GET.get('bookname')
				conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha')
				cursor=conn.cursor()
				if 'order' in request.GET:
					order=request.GET.get('order')
					if int(order)==1:
						sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' order by price limit "+str(pages)+",3;"
					else:
						sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' order by price desc limit "+str(pages)+",3;"
				else:
					sql="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%' limit "+str(pages)+",3;"
				sql1="select id,name,author,price,importdate from books_book where name like '%"+str(bookname)+"%';"
				cursor.execute("set names utf8;")
				cursor.execute(sql)
				infors=cursor.fetchall()
				ress=[]
				for infor in infors:
					ress.append({'id':infor[0],'bookname':infor[1],'author':infor[2],'price':infor[3],'importdate':infor[4]})
				count=cursor.execute(sql1)
				if count%3==0:
					number_pages=count/3
				else:
					number_pages=count/3+1
				end_pages=number_pages-1
				if int_page==0:
					has_priv=False
				else:
					has_priv=True
				if int_page==end_pages:
					has_next=False
				else:
					has_next=True	
				next_page=int_page+1
				priv_page=int_page-1
				cursor.close()
				conn.close()
				if 'order' in request.GET:
					return render_to_response('registration/delete.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname,'order':order})
				return render_to_response('registration/delete.html',{'ress':ress,'has_next':has_next,'has_priv':has_priv,'end_pages':end_pages,'next_page':next_page,'priv_page':priv_page,'bookname':bookname})
		return render_to_response('registration/delete.html',{'ress':ress,'bookname':bookname})

@login_required
def dels(request):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	if request.method=='POST' and 'id' in request.POST:
		id=request.POST.get('id').strip()
		conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha',charset='utf8')
		sql="delete from books_book where id=%d" %(int(id))
		cursor=conn.cursor()
		cursor.execute("set names utf8")
		cursor.execute(sql)
		conn.commit()
		cursor.close()
		conn.close()
	if request.method=='POST' and 'ids' in request.POST:
		ids=request.POST.get('ids').strip()
		for id in ids.split(','):
			if len(id)>0:
				conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha',charset='utf8')
				cursor=conn.cursor()
				sql="delete from books_book where id=%d" %(int(id))
				cursor.execute(sql)
				conn.commit()
		cursor.close()
		conn.close()
	return HttpResponse("")	




def excel(request):
	wb=xlwt.Workbook()
	ws=wb.add_sheet('Sheetname',cell_overwrite_ok=True)	
	style_k=xlwt.easyxf('font: bold on,colour_index green,height 360;align: wrap off;borders:left 1,right 1,top 1,bottom 1;pattern: pattern alt_bars, fore_colour gray25, back_colour gray25') 
	fnt=xlwt.Font()
	fnt.name='Arial'
	fnt.colour_index=4
	fnt.bold=True
	
	pattern=xlwt.Pattern()
	pattern.pattern=xlwt.Pattern.SOLID_PATTERN
	pattern.pattern_back_color=0x3A
	pattern.pattern_fore_colour=0x3A
	
	borders=xlwt.Borders()
	borders.left=1
	borders.right=1
	borders.top=1
	borders.bottom=1
	borders.bottom_colour=0x3A

	style=xlwt.XFStyle()
	style.font=fnt
	style.borders=borders
	style.pattern=pattern

	for i in range(2,8):
		ws.col(i).width-0xd00+2000
	
	ws.write(0,0,'Firstname',style)
	ws.write(0,0,'Firstname')
	ws.write_merge(0,1,0,1,'Firstname',style)

	style.num_format_str='YYYY-MM-DD'
	n="HYPERLINK"
	attach_report=xlwt.Formula(n+'("http://www.baidu.com";"frame.pdf")')
	fname='testfile.xls'
	agent=request.META.get('HTTP_USER_AGENT')
	if agent and re.search('MSIE',agent):
		response=HttpResponse(mimetype="application/vnd.ms-excel")
		response['Content-Disposition']='attachment;filename=%s' % urlquote(fname)
	else:
		response=HttpResponse(mimetype="application/ms-excel")
		response['Content-Disposition']='attachment;filename=%s' % smart_str(fname)
	wb.save(response)
	return response


def export(request):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	times=time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))
	conn=MySQLdb.connect(host="localhost",user="root",passwd="redhat",port=3306,db='haha',charset="utf8")
	cursor=conn.cursor()
	if request.method=='GET':
		if 'bookname' in request.GET:
			bookname=request.GET.get('bookname')
			sql="select name,author,price,importdate from books_book where name like '%"+str(bookname)+"%';"	
		if 'author' in request.GET:
			author=request.GET.get('author')
			sql="select name,author,price,importdate from books_book where author like '%"+str(author)+"%';"	
	cursor.execute(sql)
	wb=xlwt.Workbook()
	ws=wb.add_sheet(u'图书',cell_overwrite_ok=True)	
	style_k=xlwt.easyxf('font: bold on,colour_index green,height 360;align: wrap off;borders:left 1,right 1,top 1,bottom 1;pattern: pattern alt_bars, fore_colour gray25, back_colour gray25') 
	fnt=xlwt.Font()
	fnt.name='Arial'
	fnt.colour_index=4
	fnt.bold=True
	
	alignment=xlwt.Alignment()
	alignment.horz=xlwt.Alignment.HORZ_CENTER
	alignment.vert=xlwt.Alignment.VERT_CENTER
	
	
	borders=xlwt.Borders()
	borders.left=1
	borders.right=1
	borders.top=1
	borders.bottom=1

	style=xlwt.XFStyle()
	style.font=fnt
	style.borders=borders
	style.alignment=alignment
	style1=xlwt.XFStyle()
	style1.font=fnt
	style1.borders=borders
	style1.alignment=alignment
	

	for i in range(2,8):
		ws.col(i).width-0xd00+2000
	
	ws.write(0,0,u'图书名称',style)
	ws.write(0,0,u'图书名称')
	ws.write_merge(0,1,0,1,u'图书名称',style)

	ws.write(0,2,u'作者',style)
	ws.write(0,2,u'作者')
	ws.write_merge(0,1,2,3,u'作者',style)

	ws.write(0,3,u'价格(￥)',style)
	ws.write(0,3,u'价格(￥)')
	ws.write_merge(0,1,4,5,u'价格(￥)',style)

	ws.write(0,6,u'入库日期',style)
	ws.write(0,6,u'入库日期')
	ws.write_merge(0,1,6,7,u'入库日期',style)

	style.num_format_str='YYYY-MM-DD h:mm'
	n="HYPERLINK"
	infors=cursor.fetchall()
	i=2
	for infor in infors:
		ws.write(i,0,infor[0],style)
		ws.write(i,0,infor[0])
		ws.write_merge(i,i,0,1,infor[0],style)

		ws.write(i,2,infor[1],style)
		ws.write(i,2,infor[1])
		ws.write_merge(i,i,2,3,infor[1],style)

		ws.write(i,4,infor[2],style1)
		ws.write(i,4,infor[2])
		ws.write_merge(i,i,4,5,infor[2],style1)

		ws.write(i,6,infor[3],style)
		ws.write(i,6,infor[3])
		ws.write_merge(i,i,6,7,infor[3],style)
		i=i+1
		

	fname='export%s.xls' % times
	agent=request.META.get('HTTP_USER_AGENT')
	if agent and re.search('MSIE',agent):
		response=HttpResponse(mimetype="application/vnd.ms-excel")
		response['Content-Disposition']='attachment;filename=%s' % urlquote(fname)
	else:
		response=HttpResponse(mimetype="application/ms-excel")
		response['Content-Disposition']='attachment;filename=%s' % smart_str(fname)
	wb.save(response)
	return response






def upload(f):
	filename=f.name
	destination=open("upload/%s" % filename,'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()


def open_excel(file):
	try:
		data=xlrd.open_workbook(file)
		return data
	except Exception,e:
		print str(e)


@login_required
def batchs(request):
	files=open('/home/haha/haha/upload/readme.txt',"rb")
	chars=files.readlines()
	help_content=" ".join(chars)
	if request.method=='POST':
			form=uploadform(request.POST,request.FILES)
			if form.is_valid():
				times=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
				user=request.user.id
				f=request.FILES['files']
				if f.name.split('.')[1]=='txt':
					message=''
					upload(f)
					openf=open('upload/%s' % f.name,'rb')
					chars=openf.readlines()
					for char in chars:
						results=[]
						bookname=char.split(',')[0].strip()
						author=char.split(',')[1].strip()
						price=char.split(',')[2].split('\n')[0].strip()
						try:
							Book=book.objects.get(name=bookname)
						except book.DoesNotExist:
							if len(bookname)>0 and len(author)>0 and len(price)>0:
								Book=book.objects.create(name=bookname,author=author,price=price,importdate=times,user=user)
								Book.save()
							else:
								message="数据格式不正确!"
						else:
							message="图书:%s已经录入过!" % bookname
					openf.close()
						
				else:
					if f.name.split('.')[1]=='xls':
						message="excel file upload"
						upload(f)
						data=open_excel('upload/%s' % f.name)
						table=data.sheet_by_index(0)
						nrows=table.nrows
						ncols=table.ncols
						title=table.row_values(0)
						for rownum in range(2,nrows):
							record=[]
							row=table.row_values(rownum)
							for i in range(ncols):
								record.append(row[i])
							try:
								Book=book.objects.get(name=record[0])
							except book.DoesNotExist:
								Book=book.objects.create(name=record[0],author=record[2],price=record[4],importdate=times,user=user)
								Book.save()
							else:
								message="图书:%s 已经录入过！" % record[0]
					else:
						message='not supper this file'
				if message=='':
					message='图书录入成功!'
				return render_to_response('registration/batch.html',{'form':form,'message':message})
	else:
		form=uploadform()
	return render_to_response('registration/batch.html',{'form':form,'help_content':help_content})






def wocao(request):
	conn=MySQLdb.connect(host='localhost',user='root',passwd='redhat',port=3306,db='haha',charset='utf8')
	cursor=conn.cursor()
	if request.method=='POST':
		name=request.POST.get('name')
		sql="insert into message(message)values(%s)"
		cursor.execute(sql,name)
	conn.commit()
	cursor.close()
	conn.close()
		
	return HttpResponse("...............................")
