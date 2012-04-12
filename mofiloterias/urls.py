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
  
)
