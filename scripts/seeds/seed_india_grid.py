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

def seed_india_smart_grid():
    print("Clearing old test nodes...")
    FaultLog.objects.all().delete()
    TelemetryRecord.objects.all().delete()
    GridNode.objects.all().delete()

    print("Seeding India National & Regional Smart Grid Network...")

    # Root National Super Grid Hub (Central India)
    vnd00 = GridNode.objects.create(
        node_id="VND-00",
        name="Vindhyachal Super-Thermal National Grid (Central Root)",
        node_type="SUBSTATION",
        parent=None,
        latitude=24.1000,
        longitude=82.6700,
        nominal_voltage=765.0,
        max_rated_current=120.0,
        current_voltage=765.2,
        current_current=95.4,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    # Northern Region
    del01 = GridNode.objects.create(
        node_id="DEL-01",
        name="Northern Load Despatch Centre (New Delhi 765kV Hub)",
        node_type="FEEDER",
        parent=vnd00,
        latitude=28.6139,
        longitude=77.2090,
        nominal_voltage=765.0,
        max_rated_current=90.0,
        current_voltage=763.8,
        current_current=78.2,
        frequency=50.02,
        local_status=True,
        effective_status=True
    )

    bik02 = GridNode.objects.create(
        node_id="BIK-02",
        name="Bikaner Ultra Mega Solar Park (Rajasthan 400kV)",
        node_type="TRANSFORMER",
        parent=del01,
        latitude=28.0229,
        longitude=73.3119,
        nominal_voltage=400.0,
        max_rated_current=60.0,
        current_voltage=399.5,
        current_current=42.1,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    # Western Region
    mum01 = GridNode.objects.create(
        node_id="MUM-01",
        name="Western Regional Grid Hub (Mumbai 765kV Terminal)",
        node_type="FEEDER",
        parent=vnd00,
        latitude=19.0760,
        longitude=72.8777,
        nominal_voltage=765.0,
        max_rated_current=110.0,
        current_voltage=764.1,
        current_current=88.6,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    ahm02 = GridNode.objects.create(
        node_id="AHM-02",
        name="Gujarat Industrial Distribution Hub (Ahmedabad 400kV)",
        node_type="TRANSFORMER",
        parent=mum01,
        latitude=23.0225,
        longitude=72.5714,
        nominal_voltage=400.0,
        max_rated_current=75.0,
        current_voltage=398.2,
        current_current=54.3,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    # Eastern Region
    kol01 = GridNode.objects.create(
        node_id="KOL-01",
        name="Eastern Regional Despatch Hub (Kolkata 400kV)",
        node_type="FEEDER",
        parent=vnd00,
        latitude=22.5726,
        longitude=88.3639,
        nominal_voltage=400.0,
        max_rated_current=70.0,
        current_voltage=401.0,
        current_current=48.2,
        frequency=49.99,
        local_status=True,
        effective_status=True
    )

    ghy02 = GridNode.objects.create(
        node_id="GHY-02",
        name="North-East Hydro Corridor Gateway (Guwahati 220kV)",
        node_type="TRANSFORMER",
        parent=kol01,
        latitude=26.1445,
        longitude=91.7362,
        nominal_voltage=220.0,
        max_rated_current=45.0,
        current_voltage=219.4,
        current_current=32.7,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    # Southern Region
    hyd01 = GridNode.objects.create(
        node_id="HYD-01",
        name="Southern Regional Core Substation (Hyderabad 765kV)",
        node_type="FEEDER",
        parent=vnd00,
        latitude=17.3850,
        longitude=78.4867,
        nominal_voltage=765.0,
        max_rated_current=85.0,
        current_voltage=764.5,
        current_current=64.1,
        frequency=50.02,
        local_status=True,
        effective_status=True
    )

    blr02 = GridNode.objects.create(
        node_id="BLR-02",
        name="Bengaluru Tech Corridor Feeder (400kV Smart Grid)",
        node_type="TRANSFORMER",
        parent=hyd01,
        latitude=12.9716,
        longitude=77.5946,
        nominal_voltage=400.0,
        max_rated_current=65.0,
        current_voltage=398.9,
        current_current=51.8,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    chn03 = GridNode.objects.create(
        node_id="CHN-03",
        name="Chennai Coastal Distribution Pillar (230kV Feeder)",
        node_type="CONSUMER_TAP",
        parent=blr02,
        latitude=13.0827,
        longitude=80.2707,
        nominal_voltage=230.0,
        max_rated_current=50.0,
        current_voltage=229.1,
        current_current=38.4,
        frequency=50.00,
        local_status=True,
        effective_status=True
    )

    kud04 = GridNode.objects.create(
        node_id="KUD-04",
        name="Kudankulam Deep South Feeder (230kV Terminal)",
        node_type="CONSUMER_TAP",
        parent=chn03,
        latitude=8.1670,
        longitude=77.6820,
        nominal_voltage=230.0,
        max_rated_current=40.0,
        current_voltage=230.0,
        current_current=28.1,
        frequency=50.01,
        local_status=True,
        effective_status=True
    )

    print(f"Successfully seeded {GridNode.objects.count()} India Power Grid Hubs covering all 5 Electrical Regions!")

if __name__ == '__main__':
    seed_india_smart_grid()
