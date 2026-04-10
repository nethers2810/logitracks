from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import PaginationMeta
from app.schemas.master import (
    CustomerCreate,
    CustomerDeliveryConstraintCreate,
    CustomerDeliveryConstraintRead,
    CustomerDeliveryConstraintUpdate,
    CustomerRead,
    CustomerUpdate,
    ProductCreate,
    ProductPackagingCreate,
    ProductPackagingRead,
    ProductPackagingUpdate,
    ProductRead,
    ProductStackingMapCreate,
    ProductStackingMapRead,
    ProductStackingMapUpdate,
    ProductUpdate,
    StackingRuleCreate,
    StackingRuleRead,
    StackingRuleUpdate,
    TruckAxlePolicyCreate,
    TruckAxlePolicyRead,
    TruckAxlePolicyUpdate,
    TruckTypeCreate,
    TruckTypeRead,
    TruckTypeUpdate,
    VendorLaneAllocationCreate,
    VendorLaneAllocationRead,
    VendorLaneAllocationUpdate,
)
from app.services.crud import CRUDService
from app.db.models.master import (
    Customer,
    CustomerDeliveryConstraint,
    Product,
    ProductPackaging,
    ProductStackingMap,
    StackingRule,
    TruckAxlePolicy,
    TruckType,
    VendorLaneAllocation,
)

router = APIRouter(prefix="/master")

SERVICES = {
    "products": CRUDService(Product, "product_id", ["sku_code", "product_name", "category_name"], ["sku_code"]),
    "product_packaging": CRUDService(ProductPackaging, "packaging_id", ["packaging_code", "packaging_level"]),
    "stacking_rules": CRUDService(StackingRule, "stacking_rule_id", ["rule_code", "category_name"], ["rule_code"]),
    "product_stacking_maps": CRUDService(ProductStackingMap, "product_stacking_map_id", ["mapping_basis"]),
    "truck_types": CRUDService(TruckType, "truck_type_id", ["truck_code", "truck_name"], ["truck_code"]),
    "truck_axle_policies": CRUDService(TruckAxlePolicy, "truck_axle_policy_id", ["axle_config"]),
    "customers": CRUDService(Customer, "customer_id", ["customer_code", "customer_name", "city"], ["customer_code"]),
    "customer_delivery_constraints": CRUDService(CustomerDeliveryConstraint, "customer_delivery_constraint_id", ["allowed_truck_group"]),
    "vendor_lane_allocations": CRUDService(VendorLaneAllocation, "vendor_lane_allocation_id", ["customer_code", "route_code"]),
}


def _list_response(service: CRUDService, db: Session, page: int, page_size: int, sort_by: str | None, sort_order: str, q: str | None):
    items, total = service.list(db, page, page_size, sort_by, sort_order, q, filters={})
    return {"items": items, "meta": PaginationMeta(page=page, page_size=page_size, total=total)}


@router.get("/products")
def list_products(page: int = 1, page_size: int = 20, sort_by: str | None = None, sort_order: str = "asc", q: str | None = None, db: Session = Depends(get_db)):
    return _list_response(SERVICES["products"], db, page, page_size, sort_by, sort_order, q)


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return SERVICES["products"].create(db, payload.model_dump())


@router.get("/products/{entity_id}", response_model=ProductRead)
def get_product(entity_id: int, db: Session = Depends(get_db)):
    return SERVICES["products"].get(db, entity_id)


@router.put("/products/{entity_id}", response_model=ProductRead)
def update_product(entity_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    return SERVICES["products"].update(db, entity_id, payload.model_dump(exclude_unset=True))


@router.delete("/products/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(entity_id: int, db: Session = Depends(get_db)):
    SERVICES["products"].delete(db, entity_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def register_generic_routes(path: str, service_key: str, create_schema, read_schema, update_schema):
    service = SERVICES[service_key]

    @router.get(path)
    def list_entities(page: int = 1, page_size: int = 20, sort_by: str | None = None, sort_order: str = "asc", q: str | None = None, db: Session = Depends(get_db)):
        return _list_response(service, db, page, page_size, sort_by, sort_order, q)

    @router.post(path, response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_entity(payload: create_schema, db: Session = Depends(get_db)):
        return service.create(db, payload.model_dump())

    @router.get(f"{path}/{{entity_id}}", response_model=read_schema)
    def get_entity(entity_id: int, db: Session = Depends(get_db)):
        return service.get(db, entity_id)

    @router.put(f"{path}/{{entity_id}}", response_model=read_schema)
    def update_entity(entity_id: int, payload: update_schema, db: Session = Depends(get_db)):
        return service.update(db, entity_id, payload.model_dump(exclude_unset=True))

    @router.delete(f"{path}/{{entity_id}}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_entity(entity_id: int, db: Session = Depends(get_db)):
        service.delete(db, entity_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


register_generic_routes("/product-packaging", "product_packaging", ProductPackagingCreate, ProductPackagingRead, ProductPackagingUpdate)
register_generic_routes("/stacking-rules", "stacking_rules", StackingRuleCreate, StackingRuleRead, StackingRuleUpdate)
register_generic_routes("/product-stacking-maps", "product_stacking_maps", ProductStackingMapCreate, ProductStackingMapRead, ProductStackingMapUpdate)
register_generic_routes("/truck-types", "truck_types", TruckTypeCreate, TruckTypeRead, TruckTypeUpdate)
register_generic_routes("/truck-axle-policies", "truck_axle_policies", TruckAxlePolicyCreate, TruckAxlePolicyRead, TruckAxlePolicyUpdate)
register_generic_routes("/customers", "customers", CustomerCreate, CustomerRead, CustomerUpdate)
register_generic_routes("/customer-delivery-constraints", "customer_delivery_constraints", CustomerDeliveryConstraintCreate, CustomerDeliveryConstraintRead, CustomerDeliveryConstraintUpdate)
register_generic_routes("/vendor-lane-allocations", "vendor_lane_allocations", VendorLaneAllocationCreate, VendorLaneAllocationRead, VendorLaneAllocationUpdate)
