import { DataTable } from '../components/DataTable';
import { useCustomers, useProducts, useStackingRules, useTruckTypes, useVendorAllocations } from '../hooks/useApi';
import { QueryBlock } from './shared';

function Generic({ title, hook, columns }: any) {
  const { data, isLoading, isError } = hook();
  return <div className="space-y-4"><h2 className="text-2xl font-semibold">{title}</h2><QueryBlock isLoading={isLoading} isError={isError} isEmpty={!data?.length}><DataTable data={data} columns={columns}/></QueryBlock></div>;
}

export const ProductPage = () => <Generic title="Product Master" hook={useProducts} columns={[{key:'sku',header:'SKU',render:(r:any)=>r.sku_code},{key:'name',header:'Name',render:(r:any)=>r.product_name??'-'},{key:'cat',header:'Category',render:(r:any)=>r.category_name??'-'},{key:'uom',header:'Base UOM',render:(r:any)=>r.base_uom??'-'}]} />;
export const TruckTypePage = () => <Generic title="Truck Type" hook={useTruckTypes} columns={[{key:'code',header:'Code',render:(r:any)=>r.truck_code??'-'},{key:'name',header:'Truck Name',render:(r:any)=>r.truck_name??'-'},{key:'payload',header:'Payload (kg)',render:(r:any)=>r.max_payload_kg??'-'},{key:'volume',header:'Volume (m3)',render:(r:any)=>r.cargo_volume_m3??'-'}]} />;
export const StackingRulePage = () => <Generic title="Stacking Rule" hook={useStackingRules} columns={[{key:'rule',header:'Rule Code',render:(r:any)=>r.rule_code??'-'},{key:'cat',header:'Category',render:(r:any)=>r.category_name??'-'},{key:'sub',header:'Subcategory',render:(r:any)=>r.subcategory_name??'-'},{key:'max',header:'Max Layers',render:(r:any)=>r.max_stack_layer??'-'}]} />;
export const CustomerPage = () => <Generic title="Customer" hook={useCustomers} columns={[{key:'code',header:'Code',render:(r:any)=>r.customer_code??'-'},{key:'name',header:'Customer Name',render:(r:any)=>r.customer_name??'-'},{key:'city',header:'City',render:(r:any)=>r.city??'-'},{key:'zone',header:'Zone/Region',render:(r:any)=>`${r.zone??'-'} / ${r.region??'-'}`}]}/>;
export const VendorAllocationPage = () => <Generic title="Vendor Allocation" hook={useVendorAllocations} columns={[{key:'customer',header:'Customer',render:(r:any)=>r.customer_code??'-'},{key:'ship',header:'Ship-To',render:(r:any)=>r.ship_to_code??'-'},{key:'route',header:'Route',render:(r:any)=>r.route_code??'-'},{key:'truck',header:'Truck',render:(r:any)=>r.truck_name??'-'},{key:'priority',header:'Priority',render:(r:any)=>r.priority_no??'-'}]} />;
