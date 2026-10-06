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


from backend.models import District, ElectricityZone, AreaSector, GridNotification

def seed_hierarchy():
    print("[SEEDING TAMIL NADU HIERARCHY: DISTRICT -> ZONE -> AREA]")

    District.objects.all().delete()
    ElectricityZone.objects.all().delete()
    AreaSector.objects.all().delete()

    # 1. DISTRICTS
    districts_data = [
        {"district_id": "DIST_CHENNAI", "name": "Chennai", "latitude": 13.0827, "longitude": 80.2707, "total_consumers": 320000},
        {"district_id": "DIST_COIMBATORE", "name": "Coimbatore", "latitude": 11.0168, "longitude": 76.9558, "total_consumers": 210000},
        {"district_id": "DIST_MADURAI", "name": "Madurai", "latitude": 9.9252, "longitude": 78.1198, "total_consumers": 160000},
        {"district_id": "DIST_TRICHY", "name": "Tiruchirappalli", "latitude": 10.7905, "longitude": 78.7047, "total_consumers": 135000},
        {"district_id": "DIST_SALEM", "name": "Salem", "latitude": 11.6643, "longitude": 78.1460, "total_consumers": 120000},
        {"district_id": "DIST_TIRUNELVELI", "name": "Tirunelveli", "latitude": 8.7139, "longitude": 77.7567, "total_consumers": 95000},
    ]

    dist_objs = {}
    for d in districts_data:
        obj = District.objects.create(**d, is_power_on=True)
        dist_objs[d["district_id"]] = obj
        print(f"  + District: {obj.name} ({obj.district_id})")

    # 2. ZONES
    zones_data = [
        # Chennai
        {"zone_id": "ZONE_OMR", "district": dist_objs["DIST_CHENNAI"], "name": "OMR IT Corridor Zone", "latitude": 12.9348, "longitude": 80.2312},
        {"zone_id": "ZONE_TNAGAR", "district": dist_objs["DIST_CHENNAI"], "name": "Central Commercial Zone (T. Nagar)", "latitude": 13.0401, "longitude": 80.2325},
        {"zone_id": "ZONE_VELACHERY", "district": dist_objs["DIST_CHENNAI"], "name": "South Residential Zone (Velachery)", "latitude": 12.9790, "longitude": 80.2185},
        {"zone_id": "ZONE_ANNANAGAR", "district": dist_objs["DIST_CHENNAI"], "name": "North Urban Zone (Anna Nagar)", "latitude": 13.0850, "longitude": 80.2100},

        # Coimbatore
        {"zone_id": "ZONE_CBE_NORTH", "district": dist_objs["DIST_COIMBATORE"], "name": "Gandhipuram Urban Zone", "latitude": 11.0183, "longitude": 76.9680},
        {"zone_id": "ZONE_CBE_EAST", "district": dist_objs["DIST_COIMBATORE"], "name": "Peelamedu Industrial Zone", "latitude": 11.0315, "longitude": 77.0120},

        # Madurai
        {"zone_id": "ZONE_MDU_CENTRAL", "district": dist_objs["DIST_MADURAI"], "name": "Goripalayam Temple Zone", "latitude": 9.9280, "longitude": 78.1350},
        {"zone_id": "ZONE_MDU_SOUTH", "district": dist_objs["DIST_MADURAI"], "name": "Madurai South Substation Zone", "latitude": 9.9050, "longitude": 78.1150},

        # Trichy
        {"zone_id": "ZONE_TRY_ISLAND", "district": dist_objs["DIST_TRICHY"], "name": "Srirangam Heritage Island Zone", "latitude": 10.8624, "longitude": 78.6908},
        {"zone_id": "ZONE_TRY_CANTON", "district": dist_objs["DIST_TRICHY"], "name": "Cantonment Commercial Zone", "latitude": 10.8010, "longitude": 78.6850},

        # Salem
        {"zone_id": "ZONE_SLM_JUNCTION", "district": dist_objs["DIST_SALEM"], "name": "Meyyanur Junction Zone", "latitude": 11.6643, "longitude": 78.1460},

        # Tirunelveli
        {"zone_id": "ZONE_TNV_NUCLEAR", "district": dist_objs["DIST_TIRUNELVELI"], "name": "Kudankulam EHV Energy Hub", "latitude": 8.1720, "longitude": 77.6850},
    ]

    zone_objs = {}
    for z in zones_data:
        obj = ElectricityZone.objects.create(**z, is_power_on=True)
        zone_objs[z["zone_id"]] = obj
        print(f"    - Zone: {obj.name} in {obj.district.name}")

    # 3. AREAS (with ZIP/PIN, Problem Details & Maintenance)
    areas_data = [
        # OMR Zone Areas
        {
            "area_id": "AREA_SHOLINGANALLUR",
            "zone": zone_objs["ZONE_OMR"],
            "name": "Sholinganallur Junction",
            "pincode": "600119",
            "latitude": 12.9010,
            "longitude": 80.2279,
            "radius_meters": 2400,
            "total_homes": 2850,
            "main_problem_title": "11kV Cable Cut during Metro Rail Excavation",
            "main_problem_location": "Feeder Pillar #4, Junction of Rajiv Gandhi Salai & Sholinganallur Signal",
            "main_problem_cause": "CMRL Metro Rail Line 3 heavy excavation drill struck primary 11kV underground armored power cable.",
            "fault_latitude": 12.9010,
            "fault_longitude": 80.2279,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB Quick-Response Squad #7 (AE S. Murugan)",
            "maintenance_van": "Emergency Splicing Van TN-07-G-4412",
            "maintenance_step": "Normal operational standby; 24x7 monitoring active",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "area_id": "AREA_THORAIPAKKAM",
            "zone": zone_objs["ZONE_OMR"],
            "name": "Thoraipakkam Balamurugan Garden",
            "pincode": "600097",
            "latitude": 12.9348,
            "longitude": 80.2312,
            "radius_meters": 2200,
            "total_homes": 3100,
            "main_problem_title": "Distribution Transformer Oil Flashover",
            "main_problem_location": "11kV/415V DT-08, PTC Quarters Road",
            "main_problem_cause": "Excessive evening cooling load thermal rise & insulator breakdown.",
            "fault_latitude": 12.9348,
            "fault_longitude": 80.2312,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB OMR Maintenance Team B",
            "maintenance_van": "Transformer Van TN-07-K-9002",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "area_id": "AREA_PERUNGUDI",
            "zone": zone_objs["ZONE_OMR"],
            "name": "Perungudi Toll Plaza & Industrial",
            "pincode": "600096",
            "latitude": 12.9654,
            "longitude": 80.2461,
            "radius_meters": 2600,
            "total_homes": 3400,
            "main_problem_title": "Primary Substation Feeder Breaker Trip",
            "main_problem_location": "Perungudi 11kV Feeder Breaker Bay 2",
            "main_problem_cause": "Sudden industrial load imbalance on phase B.",
            "fault_latitude": 12.9654,
            "fault_longitude": 80.2461,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB Substation Squad #1",
            "maintenance_van": "Substation Van TN-07-A-1100",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # T. Nagar Zone Areas
        {
            "area_id": "AREA_PONDYBAZAAR",
            "zone": zone_objs["ZONE_TNAGAR"],
            "name": "Pondy Bazaar Pedestrian Plaza",
            "pincode": "600017",
            "latitude": 13.0401,
            "longitude": 80.2325,
            "radius_meters": 2000,
            "total_homes": 4200,
            "main_problem_title": "Shopping Mall Service Cable Overload",
            "main_problem_location": "Pondy Bazaar West 11kV RMU-03",
            "main_problem_cause": "Commercial high-power air conditioning surge blown HT switchgear fuse.",
            "fault_latitude": 13.0401,
            "fault_longitude": 80.2325,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB Central Squad #3 (AE R. Karthik)",
            "maintenance_van": "Mobile Workshop TN-01-E-9021",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },
        {
            "area_id": "AREA_PANAGALPARK",
            "zone": zone_objs["ZONE_TNAGAR"],
            "name": "Panagal Park & Usman Road",
            "pincode": "600017",
            "latitude": 13.0425,
            "longitude": 80.2355,
            "radius_meters": 2100,
            "total_homes": 3900,
            "main_problem_title": "Underground Joint Box Moisture Ingress",
            "main_problem_location": "Usman Road Flyover Pillar 14 Junction",
            "main_problem_cause": "Pre-monsoon drainage pipe leakage penetrated underground conduit joint.",
            "fault_latitude": 13.0425,
            "fault_longitude": 80.2355,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB Central Squad #4",
            "maintenance_van": "Drainage Unit TN-01-M-3211",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Velachery Zone Areas
        {
            "area_id": "AREA_VELACHERY_BYPASS",
            "zone": zone_objs["ZONE_VELACHERY"],
            "name": "Velachery 100 Feet Bypass Road",
            "pincode": "600042",
            "latitude": 12.9790,
            "longitude": 80.2185,
            "radius_meters": 2500,
            "total_homes": 2900,
            "main_problem_title": "Storm Runoff Water Ingress in LT Pillar",
            "main_problem_location": "Feeder Pillar FP-09, 100 Feet Road near Phoenix Marketcity",
            "main_problem_cause": "Road rainwater accumulation submerged 415V busbar enclosure.",
            "fault_latitude": 12.9790,
            "fault_longitude": 80.2185,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB South Squad #5 (AE V. Raman)",
            "maintenance_van": "De-watering Unit TN-09-H-3120",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Anna Nagar Zone Areas
        {
            "area_id": "AREA_ROUNDTANA",
            "zone": zone_objs["ZONE_ANNANAGAR"],
            "name": "Anna Nagar 2nd Avenue Roundtana",
            "pincode": "600040",
            "latitude": 13.0850,
            "longitude": 80.2100,
            "radius_meters": 2400,
            "total_homes": 3800,
            "main_problem_title": "Overhead Tree Branch Flashover",
            "main_problem_location": "33kV/11kV Substation Breaker #2, 2nd Avenue",
            "main_problem_cause": "Gale wind snapped gulmohar tree branch across 11kV conductor.",
            "fault_latitude": 13.0850,
            "fault_longitude": 80.2100,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TNEB North Squad #2 (AE M. Senthil)",
            "maintenance_van": "Bucket Truck TN-02-K-8114",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Coimbatore Zone Areas
        {
            "area_id": "AREA_CROSSCUT",
            "zone": zone_objs["ZONE_CBE_NORTH"],
            "name": "Cross Cut Road Commercial Hub",
            "pincode": "641012",
            "latitude": 11.0183,
            "longitude": 76.9680,
            "radius_meters": 3000,
            "total_homes": 5200,
            "main_problem_title": "Textile Inrush Surge High-Tension Fuse Blow",
            "main_problem_location": "11kV Industrial Feeder Pillar #6, Cross Cut Junction",
            "main_problem_cause": "Spinning mill high-torque induction start blown 200A HT fuse elements.",
            "fault_latitude": 11.0183,
            "fault_longitude": 76.9680,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO CBE Industrial Squad #4 (AE K. Suresh)",
            "maintenance_van": "Emergency Van TN-38-A-5521",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Madurai Zone Areas
        {
            "area_id": "AREA_VAIGAI_BANK",
            "zone": zone_objs["ZONE_MDU_CENTRAL"],
            "name": "Goripalayam Vaigai Riverbank",
            "pincode": "625002",
            "latitude": 9.9280,
            "longitude": 78.1350,
            "radius_meters": 2800,
            "total_homes": 3950,
            "main_problem_title": "Crane Boom Collision Snapped Overhead Lines",
            "main_problem_location": "11kV Pole-Mounted DT-05, Vaigai River North Bank Road",
            "main_problem_cause": "Construction crane boom clipped overhead ACSR power cables.",
            "fault_latitude": 9.9280,
            "fault_longitude": 78.1350,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO MDU Rapid Squad #8 (AE P. Kannan)",
            "maintenance_van": "Conductor Restringing Crane TN-58-B-6743",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Trichy Zone Areas
        {
            "area_id": "AREA_SRIRANGAM_AMMA",
            "zone": zone_objs["ZONE_TRY_ISLAND"],
            "name": "Srirangam Amma Mandapam Heritage Area",
            "pincode": "620006",
            "latitude": 10.8624,
            "longitude": 78.6908,
            "radius_meters": 2700,
            "total_homes": 2750,
            "main_problem_title": "Riverbank Soil Erosion Cable Joint Strain",
            "main_problem_location": "11kV River Crossing Sub-feeder #3, Amma Mandapam Road",
            "main_problem_cause": "Kaveri river flow soil scouring stressed underground cable seal.",
            "fault_latitude": 10.8624,
            "fault_longitude": 78.6908,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO TRY Island Squad #6 (AE C. Natarajan)",
            "maintenance_van": "Mobile Workshop TN-45-C-8819",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Salem Zone Areas
        {
            "area_id": "AREA_JUNCTION_MAIN",
            "zone": zone_objs["ZONE_SLM_JUNCTION"],
            "name": "Salem Railway Junction Main Road",
            "pincode": "636004",
            "latitude": 11.6643,
            "longitude": 78.1460,
            "radius_meters": 3100,
            "total_homes": 3100,
            "main_problem_title": "Switchgear Arc Flash Degradation",
            "main_problem_location": "11kV Industrial Ring Main Unit RMU-02, Junction Road",
            "main_problem_cause": "SF6 gas pressure leak caused arc flash across circuit breaker terminals.",
            "fault_latitude": 11.6643,
            "fault_longitude": 78.1460,
            "maintenance_status": "NORMAL",
            "maintenance_team": "TANGEDCO SLM Heavy Squad #1 (AE T. Ganesan)",
            "maintenance_van": "Gas Servicing Van TN-30-D-1290",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        },

        # Tirunelveli Zone Areas
        {
            "area_id": "AREA_KUDANKULAM_BAY",
            "zone": zone_objs["ZONE_TNV_NUCLEAR"],
            "name": "Kudankulam Plant Yard Feeder Bay 1",
            "pincode": "627106",
            "latitude": 8.1720,
            "longitude": 77.6850,
            "radius_meters": 3500,
            "total_homes": 1800,
            "main_problem_title": "400kV Bus Coupling Switch Bay Testing",
            "main_problem_location": "400kV Inter-tie Bus Coupling Bay 1, Kudankulam Switchyard",
            "main_problem_cause": "Scheduled statutory protective relay calibration and busbar maintenance.",
            "fault_latitude": 8.1720,
            "fault_longitude": 77.6850,
            "maintenance_status": "NORMAL",
            "maintenance_team": "NPCIL / TANGEDCO Joint EHV Specialist Team",
            "maintenance_van": "EHV Testing Lab TN-72-Z-0001",
            "maintenance_step": "Standby",
            "maintenance_progress": 100,
            "estimated_restoration_time": "0 mins"
        }
    ]

    for a in areas_data:
        AreaSector.objects.create(**a, is_power_on=True)
        print(f"      * Area: {a['name']} ({a['pincode']}) in Zone: {a['zone'].name}")

    print("\n[SUCCESS] Seeded 6 Districts, 12 Zones, and 12 Areas across Tamil Nadu with full Zip-Line hierarchy.")

if __name__ == '__main__':
    seed_hierarchy()
