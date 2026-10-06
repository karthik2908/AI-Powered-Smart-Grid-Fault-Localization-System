import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    User Profile extending Django User with operational roles and contact info.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'System Administrator'),
        ('OPERATOR', 'Grid Control Operator'),
        ('FIELD_ENGINEER', 'Field Repair Technician'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OPERATOR')
    phone_number = models.CharField(max_length=20, blank=True)
    assigned_substation = models.CharField(max_length=100, blank=True, help_text="Operating sector or zone")
    is_2fa_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class OTPVerification(models.Model):
    """
    Stores cryptographically secure time-bounded One-Time Passwords for 2FA.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    def is_valid(self):
        return (not self.is_used) and (timezone.now() <= self.expires_at) and (self.attempts < 5)

    @classmethod
    def create_for_user(cls, user, otp_code, valid_minutes=5):
        return cls.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=valid_minutes)
        )

    def __str__(self):
        return f"OTP for {self.user.username} [Valid: {self.is_valid()}]"


class GridNode(models.Model):
    """
    Represents an electrical distribution node (Substation, Feeder, Transformer, Consumer Pole).
    Organized as a self-referencing tree to reflect electrical distribution topology.
    """
    NODE_TYPE_CHOICES = [
        ('SUBSTATION', 'Primary Distribution Substation (400kV/230kV/110kV)'),
        ('FEEDER', 'Feeder Pillar / Sectionalizer (33kV/11kV)'),
        ('TRANSFORMER', 'Distribution Transformer (11kV / 415V)'),
        ('CONSUMER_TAP', 'Distribution Service Post / Pole Tap'),
        ('HOME_METER', 'Domestic Home ESP32 Smart Meter Box (230V Single Phase)'),
    ]

    node_id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    node_type = models.CharField(max_length=20, choices=NODE_TYPE_CHOICES, default='TRANSFORMER')

    # Tamil Nadu Zone, Area & Meter Box Attributes
    zone_name = models.CharField(max_length=100, blank=True, default='Chennai Zone')
    area_landmark = models.CharField(max_length=150, blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='600001')
    service_connection_no = models.CharField(max_length=50, blank=True, default='')
    esp32_device_id = models.CharField(max_length=50, blank=True, default='')
    power_units_kwh = models.FloatField(default=120.5, help_text="Total Energy Units Recorded (kWh)")
    outage_reason = models.TextField(blank=True, default='', help_text="Specific cause for power loss if de-energized")

    # Self-referencing Parent/Child topology hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text="Immediate upstream node supplying electrical power"
    )

    # Geographic coordinates (for GIS Leaflet / Mapbox rendering)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    # Electrical rated parameters
    nominal_voltage = models.FloatField(default=230.0, help_text="Nominal phase voltage (V)")
    max_rated_current = models.FloatField(default=30.0, help_text="Maximum rated continuous current (A)")

    # Real-time Telemetry states
    current_voltage = models.FloatField(default=230.0)
    current_current = models.FloatField(default=0.0)
    frequency = models.FloatField(default=50.0)

    # Operational status flags
    local_status = models.BooleanField(
        default=True,
        help_text="Physical sensor status at this node (True=Energized, False=De-energized/Faulted)"
    )
    effective_status = models.BooleanField(
        default=True,
        help_text="Calculated Zip-Line status (Local Status AND Effective Parent Status)"
    )

    last_telemetry_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def calculate_effective_status(self):
        """
        Recursive 'Zip-Line' Topology Logic:
        Effective Status(Node_n) = Local Status(Node_n) AND Effective Status(Parent)
        If the parent node is OFF or disconnected, this node cannot be logically energized.
        """
        if not self.local_status:
            return False

        if self.parent is None:
            # Substation / Root node relies purely on its own local feed
            return self.local_status

        # Evaluate parent's effective status recursively
        return self.local_status and self.parent.calculate_effective_status()

    def propagate_downstream_status(self):
        """
        Propagates effective status updates down the entire hierarchical feeder tree.
        """
        new_status = self.calculate_effective_status()
        if self.effective_status != new_status:
            self.effective_status = new_status
            self.save(update_fields=['effective_status'])

        for child in self.children.all():
            child.propagate_downstream_status()

    def __str__(self):
        return f"{self.node_id} - {self.name} ({'ON' if self.effective_status else 'OFF'})"


class TelemetryRecord(models.Model):
    """
    Time-series sensory telemetry received from IoT nodes (ESP32).
    """
    node = models.ForeignKey(GridNode, on_delete=models.CASCADE, related_name='telemetries')
    voltage = models.FloatField()
    current = models.FloatField()
    delta_voltage = models.FloatField(default=0.0)
    delta_current = models.FloatField(default=0.0)
    frequency = models.FloatField(default=50.0)
    power_factor = models.FloatField(default=0.95)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.node.node_id} @ {self.recorded_at.strftime('%H:%M:%S')} - {self.voltage}V, {self.current}A"


class FaultLog(models.Model):
    """
    Logs every localized fault event with AI classification diagnosis and lifecycle tracking.
    """
    FAULT_TYPES = [
        (0, 'Normal (Healthy)'),
        (1, 'Short Circuit (Line-to-Ground / Phase Fault)'),
        (2, 'Physical Cable Cut (Open Circuit)'),
        (3, 'Overload / High Impedance Thermal Fault'),
    ]

    SEVERITY_LEVELS = [
        ('LOW', 'Low - Advisory Warning'),
        ('MEDIUM', 'Medium - Elevated Risk'),
        ('CRITICAL', 'Critical - Immediate Outage / Fire Risk'),
    ]

    fault_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(GridNode, on_delete=models.CASCADE, related_name='fault_logs')
    fault_type = models.IntegerField(choices=FAULT_TYPES)
    severity = models.CharField(max_length=15, choices=SEVERITY_LEVELS, default='CRITICAL')
    ai_confidence = models.FloatField(help_text="Neural Network softmax probability (0.0 to 1.0)")
    diagnosis_summary = models.TextField()

    # Snapshot of telemetry at time of fault trigger
    voltage_snapshot = models.FloatField()
    current_snapshot = models.FloatField()
    delta_v_snapshot = models.FloatField()
    delta_i_snapshot = models.FloatField()

    detected_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"[{self.get_fault_type_display()}] at {self.node.name} ({self.detected_at.strftime('%Y-%m-%d %H:%M')})"


class ZoneArea(models.Model):
    """
    Represents an Area / Zone / PIN Code sector with live Current ON/OFF status,
    Main Problem pinpointing, and Working Maintenance tracking.
    """
    zone_code = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    district = models.CharField(max_length=60)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_meters = models.IntegerField(default=3000)

    # Current / Power status: True = ON, False = OFF
    is_power_on = models.BooleanField(default=True, help_text="True if Current is ON, False if Current is OFF")
    total_homes = models.IntegerField(default=1420)

    # Main Problem Pinpointing
    main_problem_title = models.CharField(max_length=150, blank=True, default='')
    main_problem_location = models.CharField(max_length=200, blank=True, default='')
    main_problem_cause = models.TextField(blank=True, default='')
    fault_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fault_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Working Maintenance Tracking
    maintenance_status = models.CharField(max_length=50, default='NORMAL') # NORMAL, CREW_DISPATCHED, IN_PROGRESS, TESTING
    maintenance_team = models.CharField(max_length=150, blank=True, default='')
    maintenance_van = models.CharField(max_length=50, blank=True, default='')
    maintenance_step = models.CharField(max_length=200, blank=True, default='')
    maintenance_progress = models.IntegerField(default=0) # 0 to 100%
    estimated_restoration_time = models.CharField(max_length=60, blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.pincode}) - {'CURRENT ON' if self.is_power_on else 'CURRENT OFF'}"


class GridNotification(models.Model):
    """
    Stores area-wise notifications for power outages, main problem details, and maintenance updates.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone_code = models.CharField(max_length=50)
    area_name = models.CharField(max_length=120)
    pincode = models.CharField(max_length=10)
    notification_type = models.CharField(max_length=30) # OUTAGE, RESTORATION, MAINTENANCE
    title = models.CharField(max_length=150)
    message = models.TextField()
    main_problem = models.CharField(max_length=250, blank=True, default='')
    maintenance_info = models.CharField(max_length=250, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.area_name}: {self.title}"


# =========================================================================
# TAMIL NADU HIERARCHY: STATE GRID -> DISTRICT -> ZONE -> AREA (ZIP-LINE)
# =========================================================================

class District(models.Model):
    """
    Level 1: Tamil Nadu District (e.g. Chennai, Coimbatore, Madurai, Trichy, Salem, Tirunelveli).
    """
    district_id = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    is_power_on = models.BooleanField(default=True, help_text="District Main Transmission Feed (True=ON, False=OFF)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    total_consumers = models.IntegerField(default=125000)

    def effective_power_on(self):
        return self.is_power_on

    def __str__(self):
        return f"District: {self.name} - {'ON' if self.is_power_on else 'OFF'}"


class ElectricityZone(models.Model):
    """
    Level 2: Electricity Zone under District (e.g. OMR IT Corridor, Central Zone, South Zone).
    """
    zone_id = models.CharField(max_length=50, unique=True, primary_key=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=120)
    is_power_on = models.BooleanField(default=True, help_text="Zone Feeder Bus (True=ON, False=OFF)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def effective_power_on(self):
        # Zip-Line Logic: Zone is effective ON only if Zone switch is ON AND parent District is ON!
        return self.is_power_on and self.district.effective_power_on()

    def __str__(self):
        return f"{self.district.name} > {self.name} - {'ON' if self.effective_power_on() else 'OFF'}"


class AreaSector(models.Model):
    """
    Level 3: Area under Zone with PIN/ZIP code, local feeder, and domestic consumers.
    """
    area_id = models.CharField(max_length=50, unique=True, primary_key=True)
    zone = models.ForeignKey(ElectricityZone, on_delete=models.CASCADE, related_name='areas')
    name = models.CharField(max_length=120)
    pincode = models.CharField(max_length=10)
    is_power_on = models.BooleanField(default=True, help_text="Area Sub-feeder switch (True=ON, False=OFF)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_meters = models.IntegerField(default=2500)
    total_homes = models.IntegerField(default=1420)

    # Main Problem Pinpointing
    main_problem_title = models.CharField(max_length=150, blank=True, default='')
    main_problem_location = models.CharField(max_length=200, blank=True, default='')
    main_problem_cause = models.TextField(blank=True, default='')
    fault_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fault_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Working Maintenance Tracking
    maintenance_status = models.CharField(max_length=50, default='NORMAL') # NORMAL, CREW_DISPATCHED, IN_PROGRESS, TESTING
    maintenance_team = models.CharField(max_length=150, blank=True, default='')
    maintenance_van = models.CharField(max_length=50, blank=True, default='')
    maintenance_step = models.CharField(max_length=200, blank=True, default='')
    maintenance_progress = models.IntegerField(default=0)
    estimated_restoration_time = models.CharField(max_length=60, blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    def effective_power_on(self):
        # Recursive Zip-Line: Effective = Area switch AND Zone switch AND District switch!
        return self.is_power_on and self.zone.effective_power_on()

    def __str__(self):
        return f"{self.zone.district.name} > {self.zone.name} > {self.name} ({self.pincode}) - {'ON' if self.effective_power_on() else 'OFF'}"

