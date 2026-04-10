from datetime import date, datetime, UTC
from decimal import Decimal

from sqlalchemy import delete

from app.core.security import hash_password
from app.db.models.auth import AppUser
from app.db.models.engine import CubicationResult, CubicationRun
from app.db.models.master import Customer, Product, ProductPackaging, StackingRule, TruckType, VendorLaneAllocation
from app.db.models.ops import OrderHeader, OrderItem
from app.db.session import SessionLocal


def run() -> None:
    db = SessionLocal()
    try:
        for model in (CubicationResult, CubicationRun, OrderItem, OrderHeader, VendorLaneAllocation, ProductPackaging, Product, StackingRule, TruckType, Customer, AppUser):
            db.execute(delete(model))
        db.commit()

        admin = AppUser(full_name="Admin User", email="admin@logitracks.local", password_hash=hash_password("admin123"), role="admin", is_active=True)
        planner = AppUser(full_name="Planner User", email="planner@logitracks.local", password_hash=hash_password("planner123"), role="planner", is_active=True)
        analyst = AppUser(full_name="Analyst User", email="analyst@logitracks.local", password_hash=hash_password("analyst123"), role="analyst", is_active=True)
        db.add_all([admin, planner, analyst])

        customer = Customer(customer_code="CUST-DEMO", customer_name="Demo Retail DC", city="Jakarta", zone="West", region="IDN", tat_days=2, is_active=True)
        db.add(customer)
        db.flush()

        p1 = Product(sku_code="SKU-1001", product_name="Sparkling Water 330ml", category_name="Beverage", subcategory_name="Water", gross_weight_kg=Decimal("0.35"), volume_m3=Decimal("0.00042"), is_active=True)
        p2 = Product(sku_code="SKU-1002", product_name="Energy Drink 250ml", category_name="Beverage", subcategory_name="Energy", gross_weight_kg=Decimal("0.30"), volume_m3=Decimal("0.00032"), is_active=True)
        db.add_all([p1, p2])
        db.flush()

        pk1 = ProductPackaging(product_id=p1.product_id, packaging_level="CASE", packaging_code="CS-1001", qty_per_pack=Decimal("24"), length_mm=Decimal("400"), width_mm=Decimal("300"), height_mm=Decimal("250"), case_volume_m3=Decimal("0.03"), gross_weight_per_pack_kg=Decimal("8.4"), is_default_shipping_pack=True)
        pk2 = ProductPackaging(product_id=p2.product_id, packaging_level="CASE", packaging_code="CS-1002", qty_per_pack=Decimal("24"), length_mm=Decimal("380"), width_mm=Decimal("280"), height_mm=Decimal("240"), case_volume_m3=Decimal("0.025"), gross_weight_per_pack_kg=Decimal("7.2"), is_default_shipping_pack=True)
        db.add_all([pk1, pk2])

        sr = StackingRule(rule_code="STACK-BEV-01", category_name="Beverage", max_stack_layer=4, max_stack_height_mm=Decimal("1600"), is_active=True)
        db.add(sr)

        tt1 = TruckType(truck_code="CDD", truck_name="Colt Diesel Double", truck_group="medium", cargo_volume_m3=Decimal("22"), deck_area_m2=Decimal("12"), max_payload_kg=Decimal("4000"), is_active=True)
        tt2 = TruckType(truck_code="FUSO", truck_name="Fuso Box", truck_group="large", cargo_volume_m3=Decimal("38"), deck_area_m2=Decimal("18"), max_payload_kg=Decimal("8000"), is_active=True)
        db.add_all([tt1, tt2])
        db.flush()

        db.add_all([
            VendorLaneAllocation(customer_code="CUST-DEMO", ship_to_code="SHIP-01", city="Jakarta", zone="West", region="IDN", route_code="JKT-W1", truck_type_id=tt1.truck_type_id, priority_no=1, is_active=True),
            VendorLaneAllocation(customer_code="CUST-DEMO", ship_to_code="SHIP-01", city="Jakarta", zone="West", region="IDN", route_code="JKT-W1", truck_type_id=tt2.truck_type_id, priority_no=2, is_active=True),
        ])

        order = OrderHeader(order_no="SAP-ORD-0001", source_order_type="SAP", source_reference_no="DEMO-IMPORT-1", customer_id=customer.customer_id, requested_delivery_date=date.today(), planned_delivery_date=date.today(), status="imported")
        db.add(order)
        db.flush()

        db.add_all([
            OrderItem(order_id=order.order_id, product_id=p1.product_id, packaging_id=pk1.packaging_id, line_no=1, qty=Decimal("120"), qty_uom="CASE", sap_delivery_qty=Decimal("120"), sap_delivery_uom="CASE", normalized_shipping_pack_qty=Decimal("120"), gross_weight_total_kg=Decimal("1008"), volume_total_m3=Decimal("3.60")),
            OrderItem(order_id=order.order_id, product_id=p2.product_id, packaging_id=pk2.packaging_id, line_no=2, qty=Decimal("100"), qty_uom="CASE", sap_delivery_qty=Decimal("100"), sap_delivery_uom="CASE", normalized_shipping_pack_qty=Decimal("100"), gross_weight_total_kg=Decimal("720"), volume_total_m3=Decimal("2.50")),
        ])
        db.flush()

        run = CubicationRun(order_id=order.order_id, algorithm_version="demo-v1", calculation_mode="stacked", status="completed", run_started_at=datetime.now(UTC), run_finished_at=datetime.now(UTC))
        db.add(run)
        db.flush()

        db.add(CubicationResult(run_id=run.run_id, recommended_truck_type_id=tt1.truck_type_id, recommendation_status="recommended", total_weight_kg=Decimal("1728"), total_volume_m3=Decimal("6.10"), total_required_floor_area_m2=Decimal("8.30"), total_stack_count=42, recommendation_reason="CDD passes weight/volume and has best score", result_json={"sample": True, "order_no": order.order_no}))

        db.commit()
        print("Seeded Stage 6 demo data: users, master data, SAP order import, and cubication output")
    finally:
        db.close()


if __name__ == "__main__":
    run()
