from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
  # Examples:
  # url(r'^$', 'mofi.views.home', name='home'),
  # url(r'^mofi/', include('mofi.foo.urls')),
  url(r'^$', 'mofiloterias.views.index'),
  url(r'^resultados$', 'mofiloterias.views.gambling_result'),
  url(r'^extractos$', 'mofiloterias.views.extractos'),
)
