from django.conf.urls import include, url

import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'socialForce.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'/login', views.login),
    url(r'/logout', views.logout),
    url(r'/current', views.current),
    url(r'/([0-9]+)', views.record),
    url(r'', views.index)
]
