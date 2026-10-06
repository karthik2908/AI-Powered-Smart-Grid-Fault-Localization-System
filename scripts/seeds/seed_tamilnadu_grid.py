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


from backend.models import GridNode, FaultLog, TelemetryRecord

def seed_tamil_nadu_complete_smart_grid():
    print("Clearing previous grid assets...")
    FaultLog.objects.all().delete()
    TelemetryRecord.objects.all().delete()
    GridNode.objects.all().delete()

    print("\n[TAMIL NADU SMART GRID SEEDING]")
    print("Populating TANGEDCO State Grid down to Home ESP32 Meter Boxes:\n")

    # 1. ROOT: Tamil Nadu State Load Despatch Centre (Guindy 400kV)
    sldc = GridNode.objects.create(
        node_id="TN-SLDC-01",
        name="TANGEDCO State Load Despatch Centre (Guindy 400kV)",
        node_type="SUBSTATION",
        zone_name="State Grid HQ",
        area_landmark="Guindy Industrial Estate, Chennai",
        pincode="600032",
        parent=None,
        latitude=13.0067,
        longitude=80.2025,
        nominal_voltage=400.0,
        max_rated_current=200.0,
        current_voltage=400.2,
        current_current=165.4,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )
    print(f"  + ROOT: {sldc.node_id} ({sldc.name})")

    # -------------------------------------------------------------
    # 2. CHENNAI SOUTH & OMR IT CORRIDOR (PIN: 600096)
    # -------------------------------------------------------------
    omr_ss = GridNode.objects.create(
        node_id="OMR-SS-01",
        name="Taramani OMR 230kV Grid Substation",
        node_type="SUBSTATION",
        zone_name="Chennai South Zone",
        area_landmark="CSIR Road, Taramani",
        pincode="600113",
        parent=sldc,
        latitude=12.9863,
        longitude=80.2432,
        nominal_voltage=230.0,
        max_rated_current=120.0,
        current_voltage=229.8,
        current_current=98.5,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    per_dt = GridNode.objects.create(
        node_id="PER-DT-02",
        name="Perungudi 11kV Distribution Transformer (DT-44)",
        node_type="TRANSFORMER",
        zone_name="OMR IT Corridor",
        area_landmark="Near Toll Gate, Rajiv Gandhi Salai (OMR)",
        pincode="600096",
        parent=omr_ss,
        latitude=12.9654,
        longitude=80.2461,
        nominal_voltage=11.0,
        max_rated_current=80.0,
        current_voltage=11.02,
        current_current=64.2,
        frequency=50.02,
        local_status=True,
        effective_status=True
    )

    omr_fdr = GridNode.objects.create(
        node_id="OMR-FDR-03",
        name="Sholinganallur Junction Feeder Pillar Box (415V LT)",
        node_type="FEEDER",
        zone_name="OMR IT Corridor",
        area_landmark="Balamurugan Garden, Thoraipakkam",
        pincode="600097",
        parent=per_dt,
        latitude=12.9348,
        longitude=80.2312,
        nominal_voltage=415.0,
        max_rated_current=60.0,
        current_voltage=414.2,
        current_current=44.8,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    # Individual Domestic Homes with ESP32 Smart Meter Box
    home_omr_1 = GridNode.objects.create(
        node_id="HOME-OMR-101",
        name="Villa 4B, Tech Enclave (Mr. Karthikeyen)",
        node_type="HOME_METER",
        zone_name="OMR IT Corridor",
        area_landmark="PTC Quarters Road, Thoraipakkam",
        pincode="600097",
        service_connection_no="SC-04-128-091",
        esp32_device_id="ESP32-METER-TN-001",
        power_units_kwh=164.8,
        parent=omr_fdr,
        latitude=12.9385,
        longitude=80.2350,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=232.4,
        current_current=4.2,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    home_omr_2 = GridNode.objects.create(
        node_id="HOME-OMR-102",
        name="Flat 2A, Saravana Enclave (Mr. Murugan)",
        node_type="HOME_METER",
        zone_name="OMR IT Corridor",
        area_landmark="Opp. AKDR Tower, OMR",
        pincode="600096",
        service_connection_no="SC-04-128-092",
        esp32_device_id="ESP32-METER-TN-002",
        power_units_kwh=128.2,
        parent=omr_fdr,
        latitude=12.9412,
        longitude=80.2378,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=231.8,
        current_current=3.1,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    home_omr_3 = GridNode.objects.create(
        node_id="HOME-OMR-103",
        name="Green House #18, Balamurugan Nagar",
        node_type="HOME_METER",
        zone_name="OMR IT Corridor",
        area_landmark="Balamurugan Nagar, Thoraipakkam",
        pincode="600097",
        service_connection_no="SC-04-128-093",
        esp32_device_id="ESP32-METER-TN-003",
        power_units_kwh=92.6,
        parent=omr_fdr,
        latitude=12.9320,
        longitude=80.2335,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=230.5,
        current_current=2.8,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    # -------------------------------------------------------------
    # 3. CHENNAI CENTRAL & T. NAGAR ZONE (PIN: 600017)
    # -------------------------------------------------------------
    tng_ss = GridNode.objects.create(
        node_id="TNG-SS-01",
        name="T. Nagar Usman Road 110kV Substation",
        node_type="SUBSTATION",
        zone_name="Chennai Central Zone",
        area_landmark="Near Panagal Park, T. Nagar",
        pincode="600017",
        parent=sldc,
        latitude=13.0418,
        longitude=80.2341,
        nominal_voltage=110.0,
        max_rated_current=110.0,
        current_voltage=109.8,
        current_current=84.5,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    tng_dt = GridNode.objects.create(
        node_id="TNG-DT-02",
        name="Ranganathan Street Distribution Transformer (11kV)",
        node_type="TRANSFORMER",
        zone_name="Chennai Central Zone",
        area_landmark="Ranganathan Street Corner",
        pincode="600017",
        parent=tng_ss,
        latitude=13.0382,
        longitude=80.2304,
        nominal_voltage=11.0,
        max_rated_current=75.0,
        current_voltage=10.98,
        current_current=58.2,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    home_tng_1 = GridNode.objects.create(
        node_id="HOME-TNG-201",
        name="Saravana Textiles Commercial Meter",
        node_type="HOME_METER",
        zone_name="Chennai Central Zone",
        area_landmark="Usman Road, T. Nagar",
        pincode="600017",
        service_connection_no="SC-02-045-110",
        esp32_device_id="ESP32-METER-TN-004",
        power_units_kwh=412.0,
        parent=tng_dt,
        latitude=13.0401,
        longitude=80.2325,
        nominal_voltage=230.0,
        max_rated_current=32.0,
        current_voltage=228.9,
        current_current=12.4,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    home_tng_2 = GridNode.objects.create(
        node_id="HOME-TNG-202",
        name="House #14, Burkit Road (Dr. Ramanathan)",
        node_type="HOME_METER",
        zone_name="Chennai Central Zone",
        area_landmark="Burkit Road, T. Nagar",
        pincode="600017",
        service_connection_no="SC-02-045-111",
        esp32_device_id="ESP32-METER-TN-005",
        power_units_kwh=142.1,
        parent=tng_dt,
        latitude=13.0360,
        longitude=80.2355,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=229.4,
        current_current=3.8,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    # -------------------------------------------------------------
    # 4. COIMBATORE ZONE (PIN: 641012)
    # -------------------------------------------------------------
    cbe_ss = GridNode.objects.create(
        node_id="CBE-SS-01",
        name="Coimbatore Peelamedu 230kV Substation",
        node_type="SUBSTATION",
        zone_name="Coimbatore Kongu Zone",
        area_landmark="Avinashi Road, Peelamedu",
        pincode="641004",
        parent=sldc,
        latitude=11.0267,
        longitude=77.0142,
        nominal_voltage=230.0,
        max_rated_current=130.0,
        current_voltage=230.4,
        current_current=92.1,
        frequency=50.02,
        local_status=True,
        effective_status=True
    )

    cbe_dt = GridNode.objects.create(
        node_id="CBE-DT-02",
        name="Gandhipuram 11kV Distribution Transformer",
        node_type="TRANSFORMER",
        zone_name="Coimbatore Kongu Zone",
        area_landmark="Cross Cut Road, Gandhipuram",
        pincode="641012",
        parent=cbe_ss,
        latitude=11.0183,
        longitude=76.9680,
        nominal_voltage=11.0,
        max_rated_current=85.0,
        current_voltage=11.01,
        current_current=61.4,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    home_cbe_1 = GridNode.objects.create(
        node_id="HOME-CBE-301",
        name="Residence #8, Cross Cut Road (Mr. Selvam)",
        node_type="HOME_METER",
        zone_name="Coimbatore Kongu Zone",
        area_landmark="Near Power House, Gandhipuram",
        pincode="641012",
        service_connection_no="SC-09-082-012",
        esp32_device_id="ESP32-METER-TN-006",
        power_units_kwh=118.5,
        parent=cbe_dt,
        latitude=11.0210,
        longitude=76.9715,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=231.2,
        current_current=3.5,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    # -------------------------------------------------------------
    # 5. MADURAI ZONE (PIN: 625020)
    # -------------------------------------------------------------
    mdu_ss = GridNode.objects.create(
        node_id="MDU-SS-01",
        name="Madurai Koodal Nagar 110kV Substation",
        node_type="SUBSTATION",
        zone_name="Madurai South Central Zone",
        area_landmark="Koodal Nagar, Madurai",
        pincode="625018",
        parent=sldc,
        latitude=9.9542,
        longitude=78.1189,
        nominal_voltage=110.0,
        max_rated_current=95.0,
        current_voltage=109.9,
        current_current=68.4,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    mdu_dt = GridNode.objects.create(
        node_id="MDU-DT-02",
        name="Anna Nagar 11kV Distribution Transformer",
        node_type="TRANSFORMER",
        zone_name="Madurai South Central Zone",
        area_landmark="80 Feet Road, Anna Nagar",
        pincode="625020",
        parent=mdu_ss,
        latitude=9.9192,
        longitude=78.1485,
        nominal_voltage=11.0,
        max_rated_current=65.0,
        current_voltage=10.99,
        current_current=44.1,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    home_mdu_1 = GridNode.objects.create(
        node_id="HOME-MDU-401",
        name="Meenakshi Nilayam #22 (Mrs. Sundari)",
        node_type="HOME_METER",
        zone_name="Madurai South Central Zone",
        area_landmark="Anna Nagar 2nd Street, Madurai",
        pincode="625020",
        service_connection_no="SC-14-063-044",
        esp32_device_id="ESP32-METER-TN-007",
        power_units_kwh=88.4,
        parent=mdu_dt,
        latitude=9.9215,
        longitude=78.1510,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=229.8,
        current_current=2.9,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    # -------------------------------------------------------------
    # 6. TRICHY, SALEM & KUDANKULAM SOUTHERN CLEAN ENERGY
    # -------------------------------------------------------------
    try_ss = GridNode.objects.create(
        node_id="TRY-SS-01",
        name="Trichy Thillai Nagar 110kV Substation",
        node_type="SUBSTATION",
        zone_name="Tiruchirappalli Delta Zone",
        area_landmark="Salai Road, Thillai Nagar, Trichy",
        pincode="620018",
        parent=sldc,
        latitude=10.8286,
        longitude=78.6854,
        nominal_voltage=110.0,
        max_rated_current=85.0,
        current_voltage=110.1,
        current_current=58.9,
        frequency=50.02,
        local_status=True,
        effective_status=True
    )

    home_try_1 = GridNode.objects.create(
        node_id="HOME-TRY-501",
        name="Srirangam Temple Heritage Home (Mr. Rangarajan)",
        node_type="HOME_METER",
        zone_name="Tiruchirappalli Delta Zone",
        area_landmark="North Chithirai Street, Srirangam",
        pincode="620006",
        service_connection_no="SC-16-092-051",
        esp32_device_id="ESP32-METER-TN-008",
        power_units_kwh=76.2,
        parent=try_ss,
        latitude=10.8624,
        longitude=78.6908,
        nominal_voltage=230.0,
        max_rated_current=16.0,
        current_voltage=230.6,
        current_current=2.4,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    slm_ss = GridNode.objects.create(
        node_id="SLM-SS-01",
        name="Salem Steel Plant 230kV Feeder Hub",
        node_type="SUBSTATION",
        zone_name="Salem Western Industrial Zone",
        area_landmark="Steel Plant Road, Salem",
        pincode="636013",
        parent=sldc,
        latitude=11.6643,
        longitude=78.1460,
        nominal_voltage=230.0,
        max_rated_current=140.0,
        current_voltage=229.5,
        current_current=105.2,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    kud_ss = GridNode.objects.create(
        node_id="KUD-SS-01",
        name="Kudankulam Nuclear & Muppandal Wind Grid Terminal",
        node_type="SUBSTATION",
        zone_name="Tirunelveli Renewable Zone",
        area_landmark="Radhapuram / Kudankulam Coastal Hub",
        pincode="627106",
        parent=sldc,
        latitude=8.1720,
        longitude=77.6850,
        nominal_voltage=400.0,
        max_rated_current=180.0,
        current_voltage=401.4,
        current_current=142.0,
        frequency=50.02,
        local_status=True,
        effective_status=True
    )

    total_count = GridNode.objects.count()
    home_count = GridNode.objects.filter(node_type="HOME_METER").count()
    print(f"\n[SUCCESS] Successfully seeded {total_count} Tamil Nadu Smart Grid nodes!")
    print(f"          Includes {home_count} domestic consumer ESP32 smart meter boxes across Chennai (OMR, T. Nagar), Coimbatore, Madurai, Trichy, Salem, and Tirunelveli.")

if __name__ == '__main__':
    seed_tamil_nadu_complete_smart_grid()
