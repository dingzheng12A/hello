from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login,logout
from django.contrib import admin
admin.autodiscover()
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/$',include(admin.site.urls)),
	(r'^accounts/$','views.login'),
	(r'^accounts/profile/$','views.profile'),
	(r'^accounts/logout/$','views.logout'),
	(r'^register/$','views.reg'),
	(r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root': '/home/haha/haha/media/'}),  
	(r'^js/(?P<path>.*)$','django.views.static.serve',{'document_root':'templates/js'}),
	(r'^code/$','views.code'),
	(r'^passwd/$','views.password'),
	(r'^test/$','views.test'),
	(r'^addbook/$','views.addbook'),
	(r'^booklist/$','views.booklist'),
	(r'^bookmod/$','views.modifybook'),
	(r'^modify/$','views.modify'),
	(r'^haha/$','views.haha'),
	(r'^update/$','views.update'),
	(r'^deletebook/$','views.deletebook'),
	(r'^delete/$','views.delete'),
	(r'^dels/$','views.dels'),
	(r'^export/$','views.export'),
	(r'^excel/$','views.excel'),
	(r'^batch/$','views.batchs'),
	(r'^wocao.jsp/$','views.wocao'),
#	(r'^tinymce/$',include('tinymce.urls')),
    # Examples:
    # url(r'^$', 'haha.views.home', name='home'),
    # url(r'^haha/', include('haha.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
