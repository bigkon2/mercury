from django.conf.urls import url
import views

urlpatterns = [
    url(r'^me$', views.MeView.as_view()),
    url(r'^currencies$', views.CurrencyView.as_view()),
    url(r'^ports$', views.PortView.as_view()),
    url(r'^associations$', views.AssociationView.as_view()),
    url(r'^certifications$', views.CertificationView.as_view()),
    url(r'^locations$', views.LocationView.as_view()),
    url(r'^accounts/user/$', views.AccountDetailsView.as_view()),
    url(r'^details/agents/$', views.AgentDetailsView.as_view()),
    url(r'^$', views.IndexView.as_view()),
]
