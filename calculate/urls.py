from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token

from mercury import urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login$', obtain_jwt_token),
    url(r'^', include(urls))
]
