from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, OTPVerification, GridNode, TelemetryRecord, FaultLog


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'assigned_substation']


class GridNodeSerializer(serializers.ModelSerializer):
    parent_id = serializers.CharField(source='parent.node_id', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = GridNode
        fields = [
            'node_id',
            'name',
            'node_type',
            'zone_name',
            'area_landmark',
            'pincode',
            'service_connection_no',
            'esp32_device_id',
            'power_units_kwh',
            'outage_reason',
            'parent_id',
            'parent_name',
            'latitude',
            'longitude',
            'nominal_voltage',
            'max_rated_current',
            'current_voltage',
            'current_current',
            'frequency',
            'local_status',
            'effective_status',
            'last_telemetry_at',
            'children_count'
        ]

    def get_children_count(self, obj):
        return obj.children.count()


class FaultLogSerializer(serializers.ModelSerializer):
    node_name = serializers.CharField(source='node.name', read_only=True)
    fault_type_label = serializers.CharField(source='get_fault_type_display', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)

    class Meta:
        model = FaultLog
        fields = [
            'fault_id',
            'node',
            'node_name',
            'fault_type',
            'fault_type_label',
            'severity',
            'ai_confidence',
            'diagnosis_summary',
            'voltage_snapshot',
            'current_snapshot',
            'delta_v_snapshot',
            'delta_i_snapshot',
            'detected_at',
            'is_resolved',
            'resolved_at',
            'resolved_by_username',
            'resolution_notes'
        ]


class TelemetryIngestSerializer(serializers.Serializer):
    node_id = serializers.CharField(max_length=50)
    voltage = serializers.FloatField()
    current = serializers.FloatField()
    delta_voltage = serializers.FloatField(default=0.0)
    delta_current = serializers.FloatField(default=0.0)
    frequency = serializers.FloatField(default=50.0)
    power_factor = serializers.FloatField(default=0.95)


class StatusMapResponseSerializer(serializers.Serializer):
    nodes = GridNodeSerializer(many=True)
    lines = serializers.ListField()
    stats = serializers.DictField()


class ZoneAreaSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ZoneArea
        model = ZoneArea
        fields = '__all__'


class GridNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import GridNotification
        model = GridNotification
        fields = '__all__'


class AreaSectorSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    district_name = serializers.CharField(source='zone.district.name', read_only=True)
    effective_status = serializers.SerializerMethodField()

    class Meta:
        from .models import AreaSector
        model = AreaSector
        fields = '__all__'

    def get_effective_status(self, obj):
        return obj.effective_power_on()


class ElectricityZoneSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    effective_status = serializers.SerializerMethodField()
    areas = AreaSectorSerializer(many=True, read_only=True)

    class Meta:
        from .models import ElectricityZone
        model = ElectricityZone
        fields = '__all__'

    def get_effective_status(self, obj):
        return obj.effective_power_on()


class DistrictSerializer(serializers.ModelSerializer):
    effective_status = serializers.SerializerMethodField()
    zones = ElectricityZoneSerializer(many=True, read_only=True)

    class Meta:
        from .models import District
        model = District
        fields = '__all__'

    def get_effective_status(self, obj):
        return obj.effective_power_on()

