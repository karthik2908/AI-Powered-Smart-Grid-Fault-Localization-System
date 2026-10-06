import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()


from backend.models import ZoneArea, GridNotification

def seed_zones():
    print("[SEEDING TAMIL NADU ZONE / ZIP AREAS & NOTIFICATIONS]")
    
    zones_data = [
        {
            "zone_code": "OMR-600096",
            "name": "Chennai - OMR IT Corridor",
            "district": "Chennai",
            "pincode": "600096",
            "latitude": 12.9348,
            "longitude": 80.2312,
            "radius_meters": 3500,
            "is_power_on": True,
            "total_homes": 3450,
            "main_problem_title": "11kV Metro Excavation Cable Cut",
            "main_problem_location": "Feeder Pillar #4, Junction of Rajiv Gandhi Salai & Sholinganallur Signal",
            "main_problem_cause": "CMRL Metro Rail Line 3 heavy excavation drill struck primary 11kV underground armored power cable.",
            "fault_latitude": 12.9348,
            "fault_longitude": 80.2312,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB Quick-Response Squad #7 (AE S. Murugan, Senior Lineman K. Palani)",
            "maintenance_van": "Emergency Splicing Van TN-07-G-4412",
            "maintenance_step": "Normal operational standby; 24x7 monitoring active",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "TNAGAR-600017",
            "name": "Chennai - T. Nagar Commercial Hub",
            "district": "Chennai",
            "pincode": "600017",
            "latitude": 13.0401,
            "longitude": 80.2325,
            "radius_meters": 2800,
            "is_power_on": True,
            "total_homes": 4120,
            "main_problem_title": "Distribution Transformer Thermal Overload",
            "main_problem_location": "11kV/415V Distribution Transformer DT-12, Pondy Bazaar West",
            "main_problem_cause": "Peak commercial shopping load thermal overload & dielectric transformer oil flashover.",
            "fault_latitude": 13.0382,
            "fault_longitude": 80.2304,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB Central Squad #3 (AE R. Karthik, Crew of 5)",
            "maintenance_van": "Transformer Mobile Repair Unit TN-01-E-9021",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "VELACHERY-600042",
            "name": "Chennai - Velachery South",
            "district": "Chennai",
            "pincode": "600042",
            "latitude": 12.9790,
            "longitude": 80.2185,
            "radius_meters": 3000,
            "is_power_on": True,
            "total_homes": 2890,
            "main_problem_title": "Underground Feeder Water Ingress",
            "main_problem_location": "Feeder Pillar FP-09, 100 Feet Bypass Road near Phoenix Marketcity",
            "main_problem_cause": "Subsurface storm runoff water ingress in 415V distribution junction enclosure.",
            "fault_latitude": 12.9790,
            "fault_longitude": 80.2185,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB South Squad #5 (AE V. Raman)",
            "maintenance_van": "Rapid Drainage & De-watering Unit TN-09-H-3120",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "ANNANAGAR-600040",
            "name": "Chennai - Anna Nagar West",
            "district": "Chennai",
            "pincode": "600040",
            "latitude": 13.0850,
            "longitude": 80.2100,
            "radius_meters": 2500,
            "is_power_on": True,
            "total_homes": 3800,
            "main_problem_title": "Overhead Tree Branch Flashover",
            "main_problem_location": "33kV/11kV Substation Sectionalizer Breaker #2, 2nd Avenue Roundtana",
            "main_problem_cause": "Overhead tree branch flashover during storm gust winds causing bus-tie trip.",
            "fault_latitude": 13.0850,
            "fault_longitude": 80.2100,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB North Squad #2 (AE M. Senthil)",
            "maintenance_van": "Aerial Bucket Truck TN-02-K-8114",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "CBE-641012",
            "name": "Coimbatore - Gandhipuram Central",
            "district": "Coimbatore",
            "pincode": "641012",
            "latitude": 11.0183,
            "longitude": 76.9680,
            "radius_meters": 3800,
            "is_power_on": True,
            "total_homes": 5200,
            "main_problem_title": "Industrial High Tension Fuse Blown",
            "main_problem_location": "11kV Industrial Feeder Pillar #6, Cross Cut Road Junction",
            "main_problem_cause": "Textile spinning mill high motor inrush current blown primary HT fuse links.",
            "fault_latitude": 11.0183,
            "fault_longitude": 76.9680,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO CBE Industrial Squad #4 (AE K. Suresh)",
            "maintenance_van": "Industrial Emergency Van TN-38-A-5521",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "MDU-625002",
            "name": "Madurai - Goripalayam Temple Dist",
            "district": "Madurai",
            "pincode": "625002",
            "latitude": 9.9280,
            "longitude": 78.1350,
            "radius_meters": 3200,
            "is_power_on": True,
            "total_homes": 3950,
            "main_problem_title": "Overhead Line Snapped by Crane",
            "main_problem_location": "11kV Pole-Mounted Transformer DT-05, Vaigai River North Bank Road",
            "main_problem_cause": "Heavy municipal crane boom clipped and snapped 11kV aluminum conductor lines.",
            "fault_latitude": 9.9280,
            "fault_longitude": 78.1350,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO MDU Rapid Squad #8 (AE P. Kannan)",
            "maintenance_van": "Conductor Restringing Crane TN-58-B-6743",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "TRY-620006",
            "name": "Trichy - Srirangam Heritage Island",
            "district": "Tiruchirappalli",
            "pincode": "620006",
            "latitude": 10.8624,
            "longitude": 78.6908,
            "radius_meters": 3100,
            "is_power_on": True,
            "total_homes": 2750,
            "main_problem_title": "Riverbank Cable Joint Strain",
            "main_problem_location": "11kV River Crossing Sub-feeder #3, Amma Mandapam Road",
            "main_problem_cause": "Kaveri riverbank soil subsidence strained underground feeder line joint.",
            "fault_latitude": 10.8624,
            "fault_longitude": 78.6908,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO TRY Island Squad #6 (AE C. Natarajan)",
            "maintenance_van": "Riverbank Mobile Workshop TN-45-C-8819",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "SLM-636004",
            "name": "Salem - Meyyanur Steel & Junction",
            "district": "Salem",
            "pincode": "636004",
            "latitude": 11.6643,
            "longitude": 78.1460,
            "radius_meters": 3500,
            "is_power_on": True,
            "total_homes": 3100,
            "main_problem_title": "Switchgear Arc Flash Degradation",
            "main_problem_location": "11kV Industrial Ring Main Unit RMU-02, Junction Main Road",
            "main_problem_cause": "Arc flash degradation on SF6 gas-insulated switchgear terminals.",
            "fault_latitude": 11.6643,
            "fault_longitude": 78.1460,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO SLM Heavy Squad #1 (AE T. Ganesan)",
            "maintenance_van": "High Voltage Gas Servicing Van TN-30-D-1290",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "zone_code": "KUD-627106",
            "name": "Tirunelveli - Kudankulam EHV Hub",
            "district": "Tirunelveli",
            "pincode": "627106",
            "latitude": 8.1720,
            "longitude": 77.6850,
            "radius_meters": 4500,
            "is_power_on": True,
            "total_homes": 1800,
            "main_problem_title": "400kV Busbar Routine Testing",
            "main_problem_location": "400kV Inter-tie Bus Coupling Switch Bay #1, Plant Yard Substation",
            "main_problem_cause": "Scheduled statutory preventive relay calibration testing.",
            "fault_latitude": 8.1720,
            "fault_longitude": 77.6850,
            "maintenance_status": "NORMAL",
            "maintenance_team": "NPCIL / TANGEDCO Joint EHV Specialist Team",
            "maintenance_van": "EHV Testing Mobile Lab TN-72-Z-0001",
            "maintenance_step": "Normal operational standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        }
    ]

    ZoneArea.objects.all().delete()
    for z in zones_data:
        ZoneArea.objects.create(**z)
        print(f"  + Seeded Zone: {z['zone_code']} - {z['name']} (PIN: {z['pincode']})")

    # Initial Welcome / System Notifications
    GridNotification.objects.all().delete()
    GridNotification.objects.create(
        zone_code="STATEWIDE",
        area_name="Tamil Nadu Grid SLDC",
        pincode="600032",
        notification_type="SYSTEM",
        title="24x7 Area-Wise Smart Grid Monitoring Active",
        message="TANGEDCO State Load Despatch Centre reports 100% nominal operation across all 9 zones. Location-aware tracking online.",
        main_problem="None (All Feeders Energized)",
        maintenance_info="All regional maintenance vans on standby."
    )
    GridNotification.objects.create(
        zone_code="OMR-600096",
        area_name="Chennai - OMR IT Corridor",
        pincode="600096",
        notification_type="RESTORATION",
        title="Current Is ON in OMR Zone (PIN: 600096)",
        message="All 11kV distribution transformers and 3,450 domestic home smart meters in OMR IT corridor are energized at 230V 50Hz.",
        main_problem="None",
        maintenance_info="Routine surveillance"
    )
    print("  + Seeded Initial Notifications.")

if __name__ == '__main__':
    seed_zones()
