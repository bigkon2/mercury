from rest_framework import serializers
import models
from time import mktime


class UserSerializer(serializers.ModelSerializer):
    iat = serializers.SerializerMethodField()
    agent_id = serializers.SerializerMethodField()

    def get_agent_id(self, obj):
        query = obj.agent_set.all()
        if query.exists():
            return query.first().pk
        return 0

    def get_iat(self, obj):
        return mktime(obj.last_login.timetuple())

    class Meta:
        model = models.User
        fields = ('id', 'username', 'iat', 'agent_id')


class CurrencySerializer(serializers.ModelSerializer):
    priceInUSD = serializers.FloatField(source='price_in_usd')

    class Meta:
        model = models.Currency
        fields = ('id', 'name', 'symbol', 'priceInUSD')


class PortSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Port


class AssociationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agentassociations


class CertificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agentcertifications


class LocationSerializer(serializers.ModelSerializer):

    symbol = serializers.SerializerMethodField()
    Ports = serializers.SerializerMethodField()

    def get_symbol(self, obj):
        if obj:
            return obj.name[:3].upper()
        return None

    def get_Ports(self, obj):
        return obj.port_set.all().values_list('pk', flat=True)

    class Meta:
        model = models.Location
        fields = ('symbol', 'id', 'name', 'Ports')
