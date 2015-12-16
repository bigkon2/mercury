from django.views.generic import TemplateView
from rest_framework import generics, views, response
import models
import serializers
from converter import Converter


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        data = super(IndexView, self).get_context_data(**kwargs)
        data['title'] = 'PricePoint - Pricing Tool'
        return data


class MeView(views.APIView):

    def get(self, request, format=None):
        serializer = serializers.UserSerializer(request.user)
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


class AccountDetailsView(views.APIView):

    def get(self, request, format=None):
        data = request.user.named_user.all()
        serializer = serializers.CorporateAccountSerializer(data, many=True)
        data = serializer.data
        data.append({'id': None, 'name': 'None'})
        return response.Response(data)


class AgentDetailsView(views.APIView):

    def get_serializer_context(self):
        return {'request': self.request}

    def get(self, request, format=None):
        service_type = request.query_params.get('serviceType')
        tariff_type = request.query_params.get('tariffType')
        origin_ports = request.query_params.getlist('originPorts')
        destination_ports = request.query_params.getlist('destinationPorts')
        location_id = request.query_params.get('locationId')
        try:
            agent_id = request.user.agent_set.first().pk
        except AttributeError:
            agent_id = 0
        if service_type == 'Freight':
            tariff_model_types = {
                'FCL_C': 'fclfreighttariff',
                'FCL_L': 'fclfreighttariff',
                'LCL': 'lclfreighttariff',
                'Air': 'airfreighttariff',
                'Road': 'roadfreighttariff'
            }
            tariff_model = tariff_model_types.get(tariff_type)
            agent_ids = self._get_freight_agents(
                origin_ports, destination_ports, tariff_model, agent_id)
        else:  # Origin
            agent_ids = self._get_origin_agents(
                location_id, agent_id,
                origin_ports if service_type == 'Origin' else destination_ports
            )
        discounts = models.Discount.objects.filter(
            agent_id__in=agent_ids, user=request.user)
        discount_map = dict()
        for disc in discounts:
            discount_map[disc.agent_id] = disc.multiplier
        for _ in agent_ids:
            if _ not in discount_map:
                discount_map[_] = 1
        agent_ids = [k for k, v in discount_map.iteritems() if v >= 0]
        data = models.Agent.objects.filter(pk__in=agent_ids)
        serializer = serializers.AgentSerializer(
            data, many=True, context=self.get_serializer_context())
        return response.Response(serializer.data)

    def _get_freight_agents(self, orig_ports, dest_ports,
                            tariff_model, agent_id):
        if agent_id:
            agent_ids = [agent_id]
        else:
            tarif_option_name = '%s__isnull' % tariff_model
            lanes = models.Lane.objects.filter(
                origin_port__in=orig_ports,
                destination_port__in=dest_ports
            )
            lanes = lanes.filter(**{tarif_option_name: False})
            agent_ids = lanes.values_list('agent_id', flat=True)
        return agent_ids

    def _get_origin_agents(self, location_id, agent_id, ports):
        if agent_id:
            agent_ids = [agent_id]
        else:
            markets = models.Location.objects.get(
                pk=location_id).markets.filter(port__in=ports)
            agent_ids = models.Tariff.objects.filter(
                market__in=markets).values_list('agent_id', flat=True)
        return agent_ids


class PriceVive(views.APIView):

    def get(self, request, format=None):
        converter = Converter()
        query_params = converter.get_params_from_query(request.query_params)
        try:
            agent_id = request.user.agent_set.first().pk
        except AttributeError:
            agent_id = 0
        tariff_model_types = {
            'FCL_C': 'fclfreighttariff',
            'FCL_L': 'fclfreighttariff',
            'LCL': 'lclfreighttariff',
            'Air': 'airfreighttariff',
            'Road': 'roadfreighttariff'
        }
        tariff_model = tariff_model_types.get(query_params['tariff_type'])
        tariff_model = '%s_set' % tariff_model
        lanes = models.Lane.objects.filter(
            destination_port_id__in=query_params['destination_ports'],
            origin_port_id__in=query_params['origin_ports'],
            archived=False,
            agent_id=agent_id
        )
        serializer = serializers.PriceByLaneSerializer(lanes, many=True)
        return response.Response(serializer.data)