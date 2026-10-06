from django.urls import path
from .views import (
    LoginWithOTPRequestView,
    VerifyOTPView,
    StatusMapView,
    TelemetryIngestView,
    SimulateFaultView,
    FaultLogListView,
    DashboardView,
    ESP32MeterReportView,
    ZoneOutageControlView,
    NearestZoneView,
    ZoneAreaListView,
    NotificationListView,
    HierarchyStatusView,
    HierarchySwitchControlView,
    FindMyAreaHierarchyView,
    AdminAuthView,
    MapboxConfigView
)

urlpatterns = [
    # Interactive Web Dashboard UI
    path('', DashboardView.as_view(), name='dashboard'),

    # 2FA Authentication & Role Access
    path('api/auth/login/', LoginWithOTPRequestView.as_view(), name='api-login-otp'),
    path('api/auth/verify-otp/', VerifyOTPView.as_view(), name='api-verify-otp'),
    path('api/auth/role/', AdminAuthView.as_view(), name='api-auth-role'),

    # Grid GIS Map & Zip-Line Topology
    path('api/nodes/status_map/', StatusMapView.as_view(), name='api-status-map'),
    path('api/nodes/<str:node_id>/simulate/', SimulateFaultView.as_view(), name='api-simulate-fault'),

    # 3-Tier Tamil Nadu Hierarchy: District -> Zone -> Area (Zip-Line Control)
    path('api/hierarchy/', HierarchyStatusView.as_view(), name='api-hierarchy-status'),
    path('api/hierarchy/switch/', HierarchySwitchControlView.as_view(), name='api-hierarchy-switch'),
    path('api/hierarchy/my-area/', FindMyAreaHierarchyView.as_view(), name='api-hierarchy-my-area'),

    # IoT Edge Telemetry & Diagnostics
    path('api/telemetry/report/', TelemetryIngestView.as_view(), name='api-telemetry-report'),
    path('api/faults/', FaultLogListView.as_view(), name='api-faults-list'),

    # ESP32 Smart Meter Box & Zone Outage Endpoints
    path('api/esp32/meter/report/', ESP32MeterReportView.as_view(), name='api-esp32-meter-report'),
    path('api/zone/<str:zone_id>/outage/', ZoneOutageControlView.as_view(), name='api-zone-outage'),

    # Area-Wise Zone / ZIP Directory & GPS Nearest Matching
    path('api/zones/', ZoneAreaListView.as_view(), name='api-zones-list'),
    path('api/zone/nearest/', NearestZoneView.as_view(), name='api-zone-nearest'),
    path('api/notifications/', NotificationListView.as_view(), name='api-notifications-list'),

    # Mapbox API Key Config & Tile Providers
    path('api/config/mapbox/', MapboxConfigView.as_view(), name='api-mapbox-config'),
]

# Explicit static files serving for offline deployments
from django.conf import settings
from django.conf.urls.static import static
if settings.STATICFILES_DIRS:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

