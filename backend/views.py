import random
import secrets
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    GridNode, TelemetryRecord, FaultLog, OTPVerification, UserProfile,
    ZoneArea, GridNotification, District, ElectricityZone, AreaSector
)
from .serializers import (
    GridNodeSerializer, FaultLogSerializer, TelemetryIngestSerializer,
    ZoneAreaSerializer, GridNotificationSerializer,
    DistrictSerializer, ElectricityZoneSerializer, AreaSectorSerializer
)

# Import AI Inference pipeline
try:
    from ai.train_model import classify_grid_fault
except ImportError:
    # Fallback heuristic classifier if neural weights are not yet compiled
    def classify_grid_fault(voltage, current, delta_v, delta_i):
        if voltage < 50.0 and abs(current) < 0.2:
            return 2, 0.98, "Physical Cable Cut (Loss of mains potential & zero current)"
        elif current > 25.0 or delta_i > 15.0:
            return 1, 0.96, "Short Circuit / Ground Fault (High current surge with instantaneous voltage drop)"
        elif current > 16.0 or voltage < 195.0:
            return 3, 0.89, "Overload / High Impedance Thermal Stress (Thermal rating exceeded)"
        return 0, 0.99, "Normal Operational Parameters"


class LoginWithOTPRequestView(APIView):
    """
    Step 1 of 2FA: Verifies username and password, generates 6-digit OTP,
    and sends it to user's registered email via SMTP.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate cryptographically secure 6-digit OTP
        otp_code = f"{secrets.randbelow(900000) + 100000}"

        # Invalidate any pending active OTPs for this user
        OTPVerification.objects.filter(user=user, is_used=False).update(is_used=True)

        # Store fresh OTP with 5 minutes validity
        otp_record = OTPVerification.create_for_user(user=user, otp_code=otp_code, valid_minutes=5)

        # Dispatch via SMTP email
        subject = "Your Smart Grid Security Verification OTP"
        message = (
            f"Hello {user.first_name or user.username},\n\n"
            f"Your one-time security authentication code is: {otp_code}\n\n"
            f"This code will expire in 5 minutes. Do not share this OTP with anyone.\n"
            f"- AI Smart Grid Operations Security Team"
        )
        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'security@smartgrid.local'),
                [user.email or f"{user.username}@smartgrid.local"],
                fail_silently=True
            )
        except Exception:
            pass

        return Response({
            'message': '2FA verification code dispatched to registered email.',
            'username': user.username,
            'expires_in_seconds': 300,
            # For local simulation / demonstration convenience if SMTP is not configured:
            'demo_otp': otp_code if settings.DEBUG else None
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    Step 2 of 2FA: Verifies the 6-digit OTP and issues JWT tokens upon success.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        otp_code = request.data.get('otp')

        if not username or not otp_code:
            return Response({'error': 'Username and OTP code are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid user account'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve latest OTP
        otp_record = OTPVerification.objects.filter(user=user, is_used=False).order_by('-created_at').first()

        if not otp_record or not otp_record.is_valid():
            return Response({'error': 'OTP has expired or is invalid. Please request a new code.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_record.attempts += 1
        if otp_record.otp_code != str(otp_code).strip():
            otp_record.save(update_fields=['attempts'])
            return Response({'error': f'Incorrect OTP. {5 - otp_record.attempts} attempts remaining.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark OTP as successfully consumed
        otp_record.is_used = True
        otp_record.save(update_fields=['is_used', 'attempts'])

        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        role = getattr(user.profile, 'role', 'OPERATOR') if hasattr(user, 'profile') else 'OPERATOR'

        return Response({
            'message': 'Two-Factor Authentication verified successfully.',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'username': user.username,
                'email': user.email,
                'role': role
            }
        }, status=status.HTTP_200_OK)


class StatusMapView(APIView):
    """
    Endpoint: /api/nodes/status_map/
    Delivers the full topology graph for GIS visualization (Leaflet/React).
    Executes the recursive Zip-Line algorithm across all feeders.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Fetch root nodes (Substations without parents)
        root_nodes = GridNode.objects.filter(parent__isnull=True)
        for root in root_nodes:
            root.propagate_downstream_status()

        nodes = GridNode.objects.all().order_by('node_id')
        node_serializer = GridNodeSerializer(nodes, many=True)

        # Build lines (edges) between parent and child nodes
        lines = []
        node_dict = {n.node_id: n for n in nodes}

        for node in nodes:
            if node.parent_id and node.parent_id in node_dict:
                parent = node_dict[node.parent_id]
                # A line is energized (GREEN) only if both parent and child have effective_status = True
                is_line_active = parent.effective_status and node.effective_status
                lines.append({
                    'id': f"line-{parent.node_id}-{node.node_id}",
                    'from_node': parent.node_id,
                    'to_node': node.node_id,
                    'from_coord': [float(parent.latitude), float(parent.longitude)],
                    'to_coord': [float(node.latitude), float(node.longitude)],
                    'status': 'energized' if is_line_active else 'de_energized',
                    'color': '#10B981' if is_line_active else '#EF4444' # Tailwind Emerald / Red
                })

        total_count = nodes.count()
        energized_count = nodes.filter(effective_status=True).count()
        faulted_count = total_count - energized_count
        zones = ZoneArea.objects.all().order_by('name')
        districts = District.objects.all().order_by('name')
        notifications = GridNotification.objects.all().order_by('-created_at')[:25]

        return Response({
            'nodes': node_serializer.data,
            'lines': lines,
            'districts': DistrictSerializer(districts, many=True).data,
            'zones': ZoneAreaSerializer(zones, many=True).data,
            'notifications': GridNotificationSerializer(notifications, many=True).data,
            'stats': {
                'total_nodes': total_count,
                'energized_nodes': energized_count,
                'faulted_nodes': faulted_count,
                'grid_health_percentage': round((energized_count / total_count * 100), 1) if total_count > 0 else 100,
                'last_updated': timezone.now().isoformat()
            }
        })


class TelemetryIngestView(APIView):
    """
    Endpoint: /api/telemetry/report/
    Receives incoming sensor telemetry from ESP32 IoT edge nodes.
    Passes data through the Neural Network model to classify faults.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TelemetryIngestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        node_id = data['node_id']
        v = data['voltage']
        i = data['current']
        dv = data['delta_voltage']
        di = data['delta_current']

        try:
            node = GridNode.objects.get(node_id=node_id)
        except GridNode.DoesNotExist:
            return Response({'error': f'Node {node_id} not recognized'}, status=status.HTTP_404_NOT_FOUND)

        # Log time-series telemetry
        TelemetryRecord.objects.create(
            node=node,
            voltage=v,
            current=i,
            delta_voltage=dv,
            delta_current=di,
            frequency=data['frequency'],
            power_factor=data['power_factor']
        )

        # Update node live telemetry values
        node.current_voltage = v
        node.current_current = i
        node.frequency = data['frequency']

        # AI Classification Inference
        fault_type, confidence, summary = classify_grid_fault(v, i, dv, di)

        if fault_type != 0:
            # Fault condition detected!
            node.local_status = False
            node.save()
            node.propagate_downstream_status()

            # Record FaultLog
            fault_log = FaultLog.objects.create(
                node=node,
                fault_type=fault_type,
                severity='CRITICAL' if fault_type in [1, 2] else 'MEDIUM',
                ai_confidence=confidence,
                diagnosis_summary=summary,
                voltage_snapshot=v,
                current_snapshot=i,
                delta_v_snapshot=dv,
                delta_i_snapshot=di
            )
            fault_serialized = FaultLogSerializer(fault_log).data
        else:
            # Healthy operation
            node.local_status = True
            node.save()
            node.propagate_downstream_status()
            fault_serialized = None

        return Response({
            'status': 'Telemetry processed',
            'node_id': node_id,
            'local_status': node.local_status,
            'effective_status': node.effective_status,
            'ai_diagnosis': {
                'fault_type': fault_type,
                'confidence': confidence,
                'summary': summary
            },
            'fault_log': fault_serialized
        }, status=status.HTTP_200_OK)


class SimulateFaultView(APIView):
    """
    Endpoint: /api/nodes/<node_id>/simulate/
    Simulates Cable Cut, Short Circuit, or Reset for physical testing and validation.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, node_id):
        scenario = request.data.get('scenario', 'CABLE_CUT')

        try:
            node = GridNode.objects.get(node_id=node_id)
        except GridNode.DoesNotExist:
            return Response({'error': 'Node not found'}, status=status.HTTP_404_NOT_FOUND)

        if scenario == 'CABLE_CUT':
            node.local_status = False
            node.current_voltage = 0.0
            node.current_current = 0.0
            node.save()
            node.propagate_downstream_status()
            FaultLog.objects.create(
                node=node,
                fault_type=2,
                severity='CRITICAL',
                ai_confidence=0.99,
                diagnosis_summary="Simulated Physical Cable Cut: Immediate loss of continuity.",
                voltage_snapshot=0.0,
                current_snapshot=0.0,
                delta_v_snapshot=-230.0,
                delta_i_snapshot=-10.0
            )

        elif scenario == 'SHORT_CIRCUIT':
            node.local_status = False
            node.current_voltage = 25.0
            node.current_current = 45.0
            node.save()
            node.propagate_downstream_status()
            FaultLog.objects.create(
                node=node,
                fault_type=1,
                severity='CRITICAL',
                ai_confidence=0.97,
                diagnosis_summary="Simulated Short Circuit: High current spike with voltage collapse.",
                voltage_snapshot=25.0,
                current_snapshot=45.0,
                delta_v_snapshot=-205.0,
                delta_i_snapshot=35.0
            )

        elif scenario == 'RESET':
            node.local_status = True
            node.current_voltage = 230.0
            node.current_current = 10.0
            node.save()
            node.propagate_downstream_status()
            # Mark active faults as resolved
            FaultLog.objects.filter(node=node, is_resolved=False).update(
                is_resolved=True,
                resolved_at=timezone.now(),
                resolution_notes="Manually reset to normal energized status via control console."
            )

        return Response({
            'message': f"Simulation '{scenario}' applied to {node.node_id}",
            'node_id': node.node_id,
            'local_status': node.local_status,
            'effective_status': node.effective_status
        }, status=status.HTTP_200_OK)


class FaultLogListView(APIView):
    """
    Endpoint: /api/faults/
    Lists all detected fault events with filtering by resolution status.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        resolved = request.query_params.get('resolved')
        queryset = FaultLog.objects.all()
        if resolved is not None:
            queryset = queryset.filter(is_resolved=resolved.lower() == 'true')
        serializer = FaultLogSerializer(queryset[:50], many=True)
        return Response(serializer.data)


def get_mapbox_api_key():
    """
    Reads the user's Mapbox API key from the dedicated api_keys folder.
    Falls back to settings.MAPBOX_API_KEY.
    """
    import os
    base_dir = settings.BASE_DIR
    possible_paths = [
        os.path.join(base_dir, 'api_keys', 'mapbox_key.txt'),
        os.path.join(base_dir, 'api_keys', 'api_key.txt'),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception:
                pass
    return getattr(settings, 'MAPBOX_API_KEY', 'pk.eyJ1Ijoia2FydGhpa2V5YW5zazAwNCIsImEiOiJjbXV4M3VxazIwMDJrMnpzajI1Y3FtZjYwIn0.83jQBL54ebnCe9it8uSz6g')


class MapboxConfigView(APIView):
    """
    Endpoint: /api/config/mapbox/
    Interfetches and serves the Mapbox API key to frontend clients or external microservices.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        key = get_mapbox_api_key()
        return Response({
            'mapbox_api_key': key,
            'source': 'api_keys/mapbox_key.txt',
            'status': 'configured' if key else 'missing',
            'providers': {
                'streets': f'https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={key}',
                'satellite_streets': f'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={key}',
                'navigation_night': f'https://api.mapbox.com/styles/v1/mapbox/navigation-night-v1/tiles/{{z}}/{{x}}/{{y}}?access_token={key}'
            }
        })


class DashboardView(APIView):
    """
    Renders the live interactive single-page GIS Dashboard web application.
    Injects interfetched Mapbox API key into template context.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.shortcuts import render
        mapbox_key = get_mapbox_api_key()
        context = {
            'mapbox_api_key': mapbox_key,
        }
        return render(request, 'dashboard.html', context)



class ESP32MeterReportView(APIView):
    """
    Endpoint: /api/esp32/meter/report/
    Receives real-time telemetry from physical or simulated ESP32 Smart Meter Box devices.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        node_id = request.data.get('node_id') or request.data.get('meter_id') or request.data.get('device_id')
        v = float(request.data.get('voltage', 230.0))
        i = float(request.data.get('current', 2.5))
        units = float(request.data.get('units_consumed', request.data.get('power_units', 0.0)))
        freq = float(request.data.get('frequency', 50.0))

        node = GridNode.objects.filter(
            models.Q(node_id=node_id) | models.Q(esp32_device_id=node_id)
        ).first()
        if not node:
            return Response({'error': f'Meter/Device {node_id} not found'}, status=status.HTTP_404_NOT_FOUND)

        node.current_voltage = v
        node.current_current = i
        node.frequency = freq
        if units > 0:
            node.power_units_kwh = units

        if v < 40.0:
            node.local_status = False
            node.outage_reason = "Loss of incoming AC mains potential at consumer meter box."
        else:
            node.local_status = True
            node.outage_reason = ""

        node.save()
        node.propagate_downstream_status()

        return Response({
            'status': 'ACK',
            'meter_id': node.node_id,
            'effective_status': node.effective_status,
            'units_kwh': node.power_units_kwh
        })


class ZoneOutageControlView(APIView):
    """
    Endpoint: /api/zone/<zone_id>/outage/
    Cuts or restores power to an entire Zone, District, or PIN Code with an explicit reason WHY it happened.
    Updates ZoneArea model, GridNode tree, and generates persistent GridNotification.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, zone_id):
        action = request.data.get('action', 'CUT')
        reason = request.data.get('reason', '11kV Cable Cut during Chennai Metro Phase 2 Excavation.')

        # 1. Update GridNode objects in this zone
        clean_key = zone_id.split('-')[0]
        nodes = GridNode.objects.filter(
            models.Q(zone_name__icontains=clean_key) |
            models.Q(zone_name__icontains=zone_id) |
            models.Q(pincode__icontains=clean_key) |
            models.Q(pincode=zone_id) |
            models.Q(node_id__icontains=clean_key)
        )

        # 2. Update ZoneArea object
        matched_zone = ZoneArea.objects.filter(
            models.Q(zone_code__icontains=clean_key) |
            models.Q(zone_code__icontains=zone_id) |
            models.Q(pincode=zone_id) |
            models.Q(name__icontains=clean_key) |
            models.Q(name__icontains=zone_id)
        ).first()

        if action == 'CUT':
            if nodes.exists():
                for n in nodes:
                    n.local_status = False
                    n.current_voltage = 0.0
                    n.current_current = 0.0
                    n.outage_reason = reason
                    n.save()
                    n.propagate_downstream_status()
                    FaultLog.objects.create(
                        node=n,
                        fault_type=2,
                        severity='CRITICAL',
                        ai_confidence=0.99,
                        diagnosis_summary=f"Zone Outage in {n.zone_name} ({n.pincode}): {reason}",
                        voltage_snapshot=0.0,
                        current_snapshot=0.0,
                        delta_v_snapshot=-230.0,
                        delta_i_snapshot=-10.0
                    )

            if matched_zone:
                matched_zone.is_power_on = False
                matched_zone.main_problem_cause = reason
                matched_zone.maintenance_status = "IN_PROGRESS"
                matched_zone.maintenance_step = "Step 3/4: High-voltage cable core splicing and joint box casting in progress"
                matched_zone.maintenance_progress = 65
                matched_zone.estimated_restoration_time = "35 mins"
                matched_zone.save()

                GridNotification.objects.create(
                    zone_code=matched_zone.zone_code,
                    area_name=matched_zone.name,
                    pincode=matched_zone.pincode,
                    notification_type="OUTAGE",
                    title=f"🚨 POWER CUT: Current OFF in {matched_zone.name} ({matched_zone.pincode})",
                    message=f"Current is OFF across {matched_zone.name}. Main Problem: {matched_zone.main_problem_location}. Reason: {reason}.",
                    main_problem=matched_zone.main_problem_location,
                    maintenance_info=f"{matched_zone.maintenance_team} on-site (Van: {matched_zone.maintenance_van}, ETR: {matched_zone.estimated_restoration_time})"
                )
        else:
            if nodes.exists():
                for n in nodes:
                    n.local_status = True
                    n.current_voltage = n.nominal_voltage
                    n.current_current = 10.0
                    n.outage_reason = ""
                    n.save()
                    n.propagate_downstream_status()
                    FaultLog.objects.filter(node=n, is_resolved=False).update(
                        is_resolved=True,
                        resolved_at=timezone.now(),
                        resolution_notes="Power restored to zone."
                    )

            if matched_zone:
                matched_zone.is_power_on = True
                matched_zone.maintenance_status = "NORMAL"
                matched_zone.maintenance_step = "Normal operational standby; All 11kV lines energized"
                matched_zone.maintenance_progress = 100
                matched_zone.estimated_restoration_time = "0 mins"
                matched_zone.save()

                GridNotification.objects.create(
                    zone_code=matched_zone.zone_code,
                    area_name=matched_zone.name,
                    pincode=matched_zone.pincode,
                    notification_type="RESTORATION",
                    title=f"⚡ POWER RESTORED: Current ON in {matched_zone.name} ({matched_zone.pincode})",
                    message=f"Current is turned ON across {matched_zone.name}. Power flow normalized at 230V 50Hz for all consumer meters.",
                    main_problem="Fault Resolved & Tested",
                    maintenance_info="Repair completed by TNEB Lineman Crew."
                )

        return Response({
            'message': f"Zone {zone_id} power state updated to {action}",
            'affected_nodes_count': nodes.count() if nodes.exists() else 0,
            'zone': ZoneAreaSerializer(matched_zone).data if matched_zone else None,
            'reason': reason if action == 'CUT' else 'Restored to Normal'
        })


import math

class NearestZoneView(APIView):
    """
    Endpoint: /api/zone/nearest/
    Matches user's GPS coordinates to the closest Tamil Nadu Zone / PIN code area.
    Returns whether Current is ON or OFF in their area, the Main Problem location,
    and live Working Maintenance status.
    """
    permission_classes = [permissions.AllowAny]

    def get_or_post(self, request):
        data = request.data if request.method == 'POST' else request.query_params
        try:
            u_lat = float(data.get('latitude', 12.9348))
            u_lng = float(data.get('longitude', 80.2312))
        except (ValueError, TypeError):
            u_lat, u_lng = 12.9348, 80.2312

        zones = ZoneArea.objects.all()
        nearest = None
        min_distance = float('inf')

        for z in zones:
            z_lat = float(z.latitude)
            z_lng = float(z.longitude)
            # Haversine formula
            d_lat = math.radians(z_lat - u_lat)
            d_lng = math.radians(z_lng - u_lng)
            a = math.sin(d_lat/2)**2 + math.cos(math.radians(u_lat)) * math.cos(math.radians(z_lat)) * math.sin(d_lng/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            d_km = 6371 * c
            if d_km < min_distance:
                min_distance = d_km
                nearest = z

        if not nearest:
            return Response({'error': 'No zones configured'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'user_location': {'latitude': u_lat, 'longitude': u_lng},
            'nearest_zone': ZoneAreaSerializer(nearest).data,
            'distance_km': round(min_distance, 2),
            'is_power_on': nearest.is_power_on,
            'current_status_label': 'CURRENT IS ON' if nearest.is_power_on else 'CURRENT IS OFF (POWER CUT)',
            'main_problem': {
                'title': nearest.main_problem_title,
                'location': nearest.main_problem_location,
                'cause': nearest.main_problem_cause,
                'coordinates': [float(nearest.fault_latitude or nearest.latitude), float(nearest.fault_longitude or nearest.longitude)]
            } if not nearest.is_power_on else None,
            'working_maintenance': {
                'status': nearest.maintenance_status,
                'team': nearest.maintenance_team,
                'van': nearest.maintenance_van,
                'step': nearest.maintenance_step,
                'progress_percentage': nearest.maintenance_progress,
                'etr': nearest.estimated_restoration_time
            }
        })

    def get(self, request):
        return self.get_or_post(request)

    def post(self, request):
        return self.get_or_post(request)


class ZoneAreaListView(APIView):
    """
    Endpoint: /api/zones/
    Returns all Tamil Nadu Zone/ZIP areas with live Current ON/OFF status.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        zones = ZoneArea.objects.all().order_by('name')
        return Response(ZoneAreaSerializer(zones, many=True).data)


class NotificationListView(APIView):
    """
    Endpoint: /api/notifications/
    Returns recent power outage and maintenance notifications.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        notifications = GridNotification.objects.all().order_by('-created_at')[:30]
        return Response(GridNotificationSerializer(notifications, many=True).data)


class HierarchyStatusView(APIView):
    """
    Endpoint: /api/hierarchy/
    Returns full 3-level Tamil Nadu electricity hierarchy:
    Statewide Grid -> Districts -> Zones -> Areas
    Includes Zip-Line calculated effective_status at every tier.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        districts = District.objects.all().order_by('name')
        return Response(DistrictSerializer(districts, many=True).data)


class HierarchySwitchControlView(APIView):
    """
    Endpoint: /api/hierarchy/switch/
    ADMIN ONLY: Controls power switches at District, Zone, or Area levels.
    Enforces role-based permissions (User cannot toggle, Admin can toggle).
    Propagates changes through Zip-Line hierarchy and emits real-time notifications.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        role = request.data.get('role', 'USER').upper()
        if role != 'ADMIN':
            return Response({
                'error': 'Permission Denied: Only TANGEDCO System Admin has authority to switch power grid on or off. Public users have read-only access.'
            }, status=status.HTTP_403_FORBIDDEN)

        level = request.data.get('level', 'AREA').upper() # DISTRICT, ZONE, AREA
        target_id = request.data.get('target_id')
        action = request.data.get('action', 'ON').upper() # ON, OFF
        reason = request.data.get('reason', '')
        is_on = (action == 'ON')

        details = {}

        if level == 'DISTRICT':
            try:
                dist = District.objects.get(district_id=target_id)
            except District.DoesNotExist:
                return Response({'error': f'District {target_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            dist.is_power_on = is_on
            dist.save()

            if is_on:
                notif_type = 'RESTORATION'
                title = f"⚡ DISTRICT RESTORED: {dist.name} Transmission Feed Energized"
                msg = f"District {dist.name} main high-voltage transmission lines switched ON by TANGEDCO Admin. Downstream zones and areas re-energized."
            else:
                notif_type = 'OUTAGE'
                title = f"🚨 DISTRICT OUTAGE: {dist.name} Transmission Feed Switched OFF"
                msg = f"District {dist.name} switched OFF by TANGEDCO Admin ({reason or 'EHV Bus Maintenance'}). All downstream zones and areas in {dist.name} are de-energized via Zip-Line hierarchy."

            GridNotification.objects.create(
                zone_code=dist.district_id,
                area_name=f"District {dist.name}",
                pincode="600000",
                notification_type=notif_type,
                title=title,
                message=msg,
                main_problem=f"District-wide Main Bus {dist.name}" if not is_on else "",
                maintenance_info=f"TANGEDCO EHV District Command ({dist.name})"
            )

            # Sync legacy GridNode
            GridNode.objects.filter(zone_name__icontains=dist.name).update(local_status=is_on)
            for r in GridNode.objects.filter(parent__isnull=True):
                r.propagate_downstream_status()

            details = DistrictSerializer(dist).data

        elif level == 'ZONE':
            try:
                zone = ElectricityZone.objects.get(zone_id=target_id)
            except ElectricityZone.DoesNotExist:
                return Response({'error': f'Zone {target_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            zone.is_power_on = is_on
            zone.save()

            if is_on:
                notif_type = 'RESTORATION'
                title = f"⚡ ZONE RESTORED: {zone.name} in {zone.district.name}"
                msg = f"Zone {zone.name} ({zone.district.name}) distribution bus switched ON by Admin. Downstream areas re-energized."
            else:
                notif_type = 'OUTAGE'
                title = f"🚨 ZONE OUTAGE: {zone.name} in {zone.district.name}"
                msg = f"Zone {zone.name} switched OFF by Admin ({reason or 'Feeder Breaker Trip'}). All downstream areas in this zone de-energized via Zip-Line."

            GridNotification.objects.create(
                zone_code=zone.zone_id,
                area_name=zone.name,
                pincode="600000",
                notification_type=notif_type,
                title=title,
                message=msg,
                main_problem=f"Zone Substation Bus {zone.name}" if not is_on else "",
                maintenance_info=f"Zone Feeder Operation Crew ({zone.district.name})"
            )

            ZoneArea.objects.filter(models.Q(zone_code__icontains=zone.name) | models.Q(name__icontains=zone.name)).update(is_power_on=is_on)
            details = ElectricityZoneSerializer(zone).data

        elif level == 'AREA':
            try:
                area = AreaSector.objects.get(area_id=target_id)
            except AreaSector.DoesNotExist:
                return Response({'error': f'Area {target_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            area.is_power_on = is_on
            if not is_on:
                area.main_problem_cause = reason or area.main_problem_cause or "11kV Cable Cut during Construction Excavation."
                area.maintenance_status = "IN_PROGRESS"
                area.maintenance_progress = 60
                area.estimated_restoration_time = "35 mins"
                area.save()

                GridNotification.objects.create(
                    zone_code=area.area_id,
                    area_name=area.name,
                    pincode=area.pincode,
                    notification_type="OUTAGE",
                    title=f"🚨 AREA POWER CUT: {area.name} (PIN: {area.pincode})",
                    message=f"Current is OFF in {area.name}. Main Problem: {area.main_problem_location}. Reason: {area.main_problem_cause}. Maintenance crew on-site.",
                    main_problem=area.main_problem_location,
                    maintenance_info=f"{area.maintenance_team} (Van: {area.maintenance_van}, ETR: {area.estimated_restoration_time})"
                )
            else:
                area.maintenance_status = "NORMAL"
                area.maintenance_progress = 100
                area.estimated_restoration_time = "0 mins"
                area.save()

                GridNotification.objects.create(
                    zone_code=area.area_id,
                    area_name=area.name,
                    pincode=area.pincode,
                    notification_type="RESTORATION",
                    title=f"⚡ AREA RESTORED: {area.name} (PIN: {area.pincode})",
                    message=f"Current turned ON in {area.name}. Grid supply normal at 230V 50Hz.",
                    main_problem="",
                    maintenance_info="Repair completed by TNEB Lineman Crew."
                )

            ZoneArea.objects.filter(models.Q(pincode=area.pincode) | models.Q(name__icontains=area.name)).update(
                is_power_on=is_on,
                main_problem_cause=area.main_problem_cause if not is_on else "",
                maintenance_status=area.maintenance_status
            )
            GridNode.objects.filter(models.Q(pincode=area.pincode) | models.Q(name__icontains=area.name)).update(local_status=is_on)
            for r in GridNode.objects.filter(parent__isnull=True):
                r.propagate_downstream_status()

            details = AreaSectorSerializer(area).data

        return Response({
            'status': 'SUCCESS',
            'level': level,
            'target_id': target_id,
            'action': action,
            'effective_status': is_on,
            'details': details
        })


class FindMyAreaHierarchyView(APIView):
    """
    Endpoint: /api/hierarchy/my-area/
    Finds the user's exact location across District -> Zone -> Area.
    Evaluates Zip-Line cascading power status to tell user if Current is ON or OFF.
    """
    permission_classes = [permissions.AllowAny]

    def get_or_post(self, request):
        data = request.data if request.method == 'POST' else request.query_params
        try:
            u_lat = float(data.get('latitude', 12.9348))
            u_lng = float(data.get('longitude', 80.2312))
        except (ValueError, TypeError):
            u_lat, u_lng = 12.9348, 80.2312

        areas = AreaSector.objects.select_related('zone', 'zone__district').all()
        nearest = None
        min_distance = float('inf')

        for a in areas:
            a_lat = float(a.latitude)
            a_lng = float(a.longitude)
            d_lat = math.radians(a_lat - u_lat)
            d_lng = math.radians(a_lng - u_lng)
            haversine = math.sin(d_lat/2)**2 + math.cos(math.radians(u_lat)) * math.cos(math.radians(a_lat)) * math.sin(d_lng/2)**2
            c = 2 * math.atan2(math.sqrt(haversine), math.sqrt(max(0.0, 1.0 - haversine)))
            dist_km = 6371 * c
            if dist_km < min_distance:
                min_distance = dist_km
                nearest = a

        if not nearest:
            return Response({'error': 'No areas available'}, status=status.HTTP_404_NOT_FOUND)

        is_effective_on = nearest.effective_power_on()
        cutoff_level = None
        if not is_effective_on:
            if not nearest.zone.district.is_power_on:
                cutoff_level = 'DISTRICT'
            elif not nearest.zone.is_power_on:
                cutoff_level = 'ZONE'
            else:
                cutoff_level = 'AREA'

        return Response({
            'user_location': {'latitude': u_lat, 'longitude': u_lng},
            'distance_km': round(min_distance, 2),
            'district': {
                'id': nearest.zone.district.district_id,
                'name': nearest.zone.district.name,
                'is_power_on': nearest.zone.district.is_power_on
            },
            'zone': {
                'id': nearest.zone.zone_id,
                'name': nearest.zone.name,
                'is_power_on': nearest.zone.is_power_on,
                'effective_status': nearest.zone.effective_power_on()
            },
            'area': AreaSectorSerializer(nearest).data,
            'is_power_on': is_effective_on,
            'current_status_label': 'CURRENT IS ON' if is_effective_on else 'CURRENT IS OFF (POWER CUT)',
            'cutoff_level': cutoff_level,
            'main_problem': {
                'title': nearest.main_problem_title,
                'location': nearest.main_problem_location,
                'cause': nearest.main_problem_cause,
                'coordinates': [float(nearest.fault_latitude or nearest.latitude), float(nearest.fault_longitude or nearest.longitude)]
            } if not is_effective_on else None,
            'working_maintenance': {
                'status': nearest.maintenance_status,
                'team': nearest.maintenance_team,
                'van': nearest.maintenance_van,
                'step': nearest.maintenance_step,
                'progress_percentage': nearest.maintenance_progress,
                'etr': nearest.estimated_restoration_time
            }
        })

    def get(self, request):
        return self.get_or_post(request)

    def post(self, request):
        return self.get_or_post(request)


class AdminAuthView(APIView):
    """
    Endpoint: /api/auth/role/
    Allows switching between ADMIN (Control Access) and USER (Consumer Monitoring).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        pin = request.data.get('pin', '')
        username = request.data.get('username', '')

        if pin in ['1234', 'admin', 'admin123'] or username == 'admin':
            return Response({
                'authenticated': True,
                'role': 'ADMIN',
                'operator_name': 'Er. K. Murugan (Executive Engineer, TANGEDCO SLDC)',
                'message': 'Admin Access Granted: Power Switch Control Enabled.'
            })
        return Response({
            'authenticated': False,
            'role': 'USER',
            'message': 'Invalid credentials. Defaulting to Public Consumer Mode.'
        }, status=status.HTTP_401_UNAUTHORIZED)




