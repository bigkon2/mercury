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
    Ports = serializers.PrimaryKeyRelatedField(
        many=True, source='port_set', read_only=True)

    def get_symbol(self, obj):
        if obj:
            return obj.name[:3].upper()
        return None

    class Meta:
        model = models.Location
        fields = ('symbol', 'id', 'name', 'Ports')


class CorporateAccountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        user = obj.user
        full_name = ''
        if user.firstname:
            full_name += '%s ' % user.firstname
        if user.lastname:
            full_name += user.lastname
        return full_name or user.username

    class Meta:
        model = models.Corporateaccount
        fields = ('id', 'name')


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agent
        fields = ('id', 'name')
