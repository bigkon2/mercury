from django.views.generic import TemplateView
from rest_framework import generics, views, response
import models, serializers


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

    def get(self, request, format=None):
        service_type = request.query_params.get('serviceType')
        tariff_type = request.query_params.get('tariffType')
        origin_ports = request.query_params.getlist('originPorts')
        destination_ports = request.query_params.getlist('destinationPorts')
        location_id = request.query_params.get('locationId')

        tariff_model_types = {
            'FCL_C': models.Fclfreighttariff,
            'FCL_L': models.Fclfreighttariff,
            'LCL': models.Lclfreighttariff,
            'Air': models.Airfreighttariff,
            'Road': models.Roadfreighttariff
        }
        tariff_model = tariff_model_types.get(tariff_type)
        try:
            agent_id = request.user.agent_set.first().pk
        except AttributeError:
            agent_id = 0
        if service_type == 'Freight':
            data = self._get_freight_data(request,
                                          origin_ports, destination_ports,
                                          tariff_model, agent_id)
        else:  # Origin
            data = self._get_origin_data(
                request, location_id,
                origin_ports if service_type == 'Origin' else destination_ports,
                tariff_type, agent_id
            )
        serializer = serializers.AgentSerializer(data, many=True)
        return response.Response(serializer.data)


    def _get_freight_data(self, request, orig_ports, dest_ports,
                          tariff_model, agent_id):
        if agent_id:
            agent_ids = [agent_id]
        else:
            agent_ids = set()
            lanes = models.Lane.objects.filter(
                origin_port__in=orig_ports,
                destination_port__in=dest_ports
            )
            for lane in lanes:
                if tariff_model.objects.filter(lane=lane):
                    agent_ids.add(lane.agent_id)
        discounts = models.Discount.objects.filter(
            agent_id__in=agent_ids, user=request.user)
        discount_map = dict()
        for disc in discounts:
            discount_map[disc.agent_id] = disc.multiplier
        for _ in agent_ids:
            if _ not in discount_map:
                discount_map[agent_ids] = 1
        agent_ids = filter(lambda x: x >= 0, discount_map.keys())
        agents = models.Agent.objects.filter(pk__in=agent_ids)
        return agents

    def _get_origin_data(self, request, location_id, ports,
                         tariff_type, agent_id):
        if agent_id:
            agent_ids = [agent_id]
        else:
            markets = models.Location.objects.get(
                pk=location_id).markets.filter(port__in=ports)
            agent_ids = models.Tariff.objects.filter(
                market__in=markets).values_list('agent_id', flat=True)
        discounts = models.Discount.objects.filter(
            agent_id__in=agent_ids, user=request.user)
        discount_map = dict()
        for disc in discounts:
            discount_map[disc.agent_id] = disc.multiplier
        for _ in agent_ids:
            if _ not in discount_map:
                discount_map[agent_ids] = 1
        agent_ids = filter(lambda x: x >= 0, discount_map.keys())
        agents = models.Agent.objects.filter(pk__in=agent_ids)
        return agents
