from time import mktime
from django.db.models import Avg, Count
from rest_framework import serializers
import models


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
    logo = serializers.StringRelatedField(source='agentlogo.logo')
    certifications = CertificationSerializer(many=True, read_only=True)
    associations = AssociationSerializer(many=True, read_only=True)
    ratings = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        user = self.context['request'].user
        query = obj.agentrating_set.filter(agent=obj)
        data = query.exclude(user=user).aggregate(
            Avg('user_rating'), Count('id'))
        try:
            user_rating = query.get(user=user).user_rating
        except models.Agentrating.DoesNotExist:
            user_rating = 0
        return dict(
            average=data['user_rating__avg'] or 0,
            users=data['id__count'],
            user_rating=user_rating
        )

    class Meta:
        model = models.Agent
        fields = ('id', 'name', 'logo', 'certifications',
                  'associations', 'ratings')


class SimpleAgentSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(source='manager_contact')
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.email or obj.manager_email

    def get_phone(self, obj):
        return obj.phone or obj.manager_phone

    class Meta:
        model = models.Agent
        fields = ('id', 'contact', 'email', 'name', 'phone')


class PriceByLaneSerializer(serializers.ModelSerializer):
    Ports = ''
    agent_details = SimpleAgentSerializer()
    chargeable_volume = ''
    chargeable_weight = ''
    converted_rate = ''
    currency_id = ''
    marketId = ''
    maximumVolume = ''
    minimumVolume = ''
    rate = ''
    tariffId = ''
    thc = ''
