from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

  # Examples:
  # url(r'^$', 'mofi.views.home', name='home'),
  # url(r'^mofi/', include('mofi.foo.urls')),
  url(r'^$', 'mofiloterias.views.index'),
  url(r'^events$', 'mofiloterias.views.events'),
  
  url(r'^resultados$', 'gamblings.views.gambling_result'),
  url(r'^extractos$', 'gamblings.views.gambling_summaries'),  
  url(r'^importar$', 'gamblings.views.gambling_import'),

  url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
  url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

)
