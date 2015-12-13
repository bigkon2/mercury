from django.views.generic import TemplateView
from rest_framework import generics, views, response
from rest_framework.generics import get_object_or_404
import models, serializers


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        data = super(IndexView, self).get_context_data(**kwargs)
        data['title'] = 'PricePoint - Pricing Tool'
        return data


class MeView(views.APIView):

    def get(self, request, format=None):
        user = get_object_or_404(models.User.objects.all(), pk=self.request.user.pk)
        serializer = serializers.UserSerializer(user)
        return response.Response(serializer.data)


class CurrencyView(generics.ListAPIView):
    queryset = models.Currency.objects.all()
    serializer_class = serializers.CurrencySerializer


class PortView(generics.ListAPIView):
    queryset = models.Port.objects.all()
    serializer_class = serializers.PortSerializer


class AssociationView(generics.ListAPIView):
    queryset = models.Agentassociations.objects.all()
    serializer_class = serializers.AssociationSerializer


class CertificationView(generics.ListAPIView):
    queryset = models.Agentcertifications.objects.all()
    serializer_class = serializers.CertificationSerializer


class LocationView(generics.ListAPIView):
    queryset = models.Location.objects.all().order_by('name')
    serializer_class = serializers.LocationSerializer
