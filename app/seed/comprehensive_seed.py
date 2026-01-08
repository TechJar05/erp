import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import (
    Organization, Plant, Warehouse,
    Item, Vendor, VendorItem,
    InventoryBalance,
    Customer, SalesOrder, SalesOrderItem,
    Machine,
    Role, AppUser, Task, DataContext, ContextSession,
    AutomationRule
)
from uuid import UUID

def commit(db: Session):
    db.commit()

def comprehensive_seed():
    """Seed database with comprehensive test data - ADDITIVE approach"""
    db = SessionLocal()

    try:
        print("🌱 Starting comprehensive data seeding (additive mode)...")
        
        # 🧹 Only clear data that we'll recreate
        print("🧹 Clearing only transactional data...")
        db.query(Task).delete()
        db.query(SalesOrderItem).delete()
        db.query(SalesOrder).delete()
        db.query(InventoryBalance).delete()
        db.query(VendorItem).delete()
        commit(db)
        
        # 1️⃣ Get or Create Organization
        print("📊 Getting organization...")
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="Demo Manufacturing Ltd", industry="Manufacturing")
            db.add(org)
            commit(db)
        
        # 2️⃣ Get existing or create plants
        print("🏭 Getting plants...")
        plants = db.query(Plant).all()
        
        while len(plants) < 3:
            new_plant = Plant(
                organization_id=org.id,
                name=f"Plant {chr(65 + len(plants))} - {'Mumbai' if len(plants)==0 else 'Delhi' if len(plants)==1 else 'Bangalore'}",
                location={'Mumbai', 'Delhi', 'Bangalore'}[len(plants) % 3],
                timezone="Asia/Kolkata"
            )
            db.add(new_plant)
            commit(db)
            plants = db.query(Plant).all()
        
        # 3️⃣ Get existing or create warehouses
        print("📦 Getting warehouses...")
        warehouses = db.query(Warehouse).all()
        
        if len(warehouses) < 6:
            new_warehouses = [
                Warehouse(plant_id=plants[0].id, name="Mumbai - Raw Materials", type="RAW"),
                Warehouse(plant_id=plants[0].id, name="Mumbai - WIP", type="WIP"),
                Warehouse(plant_id=plants[0].id, name="Mumbai - Finished Goods", type="FINISHED"),
                Warehouse(plant_id=plants[1].id, name="Delhi - Raw Materials", type="RAW"),
                Warehouse(plant_id=plants[1].id, name="Delhi - Finished Goods", type="FINISHED"),
                Warehouse(plant_id=plants[2].id, name="Bangalore - Finished Goods", type="FINISHED"),
            ]
            db.add_all(new_warehouses)
            commit(db)
            warehouses = db.query(Warehouse).all()
        
        # 4️⃣ Get existing or create items
        print("🔧 Getting items...")
        existing_items = db.query(Item).all()
        
        if len(existing_items) < 15:
            print("   Creating additional items...")
            new_items_data = [
                ("RM-003", "Aluminum Sheet", "RAW", "KG", 400, 150),
                ("RM-004", "Copper Wire", "RAW", "METER", 1000, 300),
                ("RM-005", "Rubber Gasket", "RAW", "PCS", 200, 50),
                ("WIP-001", "Gear Assembly (In Progress)", "WIP", "PCS", 50, 20),
                ("WIP-002", "Motor Housing (In Progress)", "WIP", "PCS", 30, 10),
                ("FG-003", "Electric Motor 5HP", "FINISHED", "PCS", 60, 25),
                ("FG-004", "Hydraulic Pump", "FINISHED", "PCS", 40, 15),
                ("FG-005", "Control Panel", "FINISHED", "PCS", 50, 20),
                ("FG-006", "Premium CNC Machine", "FINISHED", "PCS", 5, 2),
                ("FG-007", "Industrial Robot Arm", "FINISHED", "PCS", 3, 1),
                ("FG-008", "Standard Bolt Kit", "FINISHED", "SET", 500, 200),
            ]
            
            for sku, name, item_type, uom, reorder, safety in new_items_data:
                existing = db.query(Item).filter(Item.sku == sku).first()
                if not existing:
                    db.add(Item(sku=sku, name=name, item_type=item_type, uom=uom, 
                               reorder_level=reorder, safety_stock=safety))
            commit(db)
        
        items = db.query(Item).order_by(Item.sku).all()
        print(f"   Total items: {len(items)}")
        
        # 5️⃣ Create diverse inventory balances
        print("📊 Creating inventory balances...")
        
        # Ensure we have enough items and warehouses
        if len(items) >= 10 and len(warehouses) >= 6:
            balances = [
                # CRITICAL LOW STOCK
                InventoryBalance(item_id=items[0].id, warehouse_id=warehouses[0].id, quantity_on_hand=150),
                InventoryBalance(item_id=items[1].id, warehouse_id=warehouses[0].id, quantity_on_hand=50),
                
                # LOW STOCK
                InventoryBalance(item_id=items[2].id, warehouse_id=warehouses[0].id, quantity_on_hand=250),
                InventoryBalance(item_id=items[3].id, warehouse_id=warehouses[0].id, quantity_on_hand=350),
                
                # HEALTHY STOCK
                InventoryBalance(item_id=items[4].id, warehouse_id=warehouses[0].id, quantity_on_hand=500),
                
                # OVERSTOCK
                InventoryBalance(item_id=items[5].id, warehouse_id=warehouses[2].id, quantity_on_hand=800),
                InventoryBalance(item_id=items[6].id, warehouse_id=warehouses[2].id, quantity_on_hand=600),
                
                # ZERO STOCK
                InventoryBalance(item_id=items[7].id, warehouse_id=warehouses[5].id, quantity_on_hand=0),
                
                # Multiple warehouses - same item
                InventoryBalance(item_id=items[8].id, warehouse_id=warehouses[2].id, quantity_on_hand=120),
                InventoryBalance(item_id=items[8].id, warehouse_id=warehouses[4].id, quantity_on_hand=80),
                InventoryBalance(item_id=items[8].id, warehouse_id=warehouses[5].id, quantity_on_hand=45),
                
                # WIP items
                InventoryBalance(item_id=items[9].id, warehouse_id=warehouses[1].id, quantity_on_hand=35),
            ]
            
            # Add more if we have more items
            if len(items) > 12:
                balances.extend([
                    InventoryBalance(item_id=items[10].id, warehouse_id=warehouses[1].id, quantity_on_hand=25),
                    InventoryBalance(item_id=items[11].id, warehouse_id=warehouses[2].id, quantity_on_hand=650),
                    InventoryBalance(item_id=items[12].id, warehouse_id=warehouses[5].id, quantity_on_hand=4),
                ])
            
            db.add_all(balances)
            commit(db)
            print(f"   Created {len(balances)} inventory balance records")
        
        # 6️⃣ Get or create vendors
        print("🏢 Getting vendors...")
        vendors = db.query(Vendor).all()
        
        if len(vendors) < 5:
            vendor_data = [
                ("SteelCorp India", "Mumbai", 4.5, 5),
                ("PolyPlast Ltd", "Delhi", 4.2, 7),
                ("MetalWorks Inc", "Pune", 4.7, 3),
                ("ElectroSupply Co", "Bangalore", 4.0, 10),
                ("QuickParts Express", "Chennai", 4.8, 2),
            ]
            
            for name, location, rating, lead_time in vendor_data:
                existing = db.query(Vendor).filter(Vendor.name == name).first()
                if not existing:
                    db.add(Vendor(name=name, location=location, rating=rating, lead_time_days=lead_time))
            commit(db)
            vendors = db.query(Vendor).all()
        
        # 7️⃣ Vendor pricing
        print("💰 Creating vendor pricing...")
        if len(vendors) >= 3 and len(items) >= 3:
            vendor_items = [
                VendorItem(vendor_id=vendors[0].id, item_id=items[0].id, unit_price=55),
                VendorItem(vendor_id=vendors[2].id, item_id=items[0].id, unit_price=52),
                VendorItem(vendor_id=vendors[1].id, item_id=items[1].id, unit_price=40),
            ]
            db.add_all(vendor_items)
            commit(db)
        
        # 8️⃣ Get or create customers
        print("👥 Getting customers...")
        customers = db.query(Customer).all()
        
        if len(customers) < 8:
            customer_data = [
                ("ABC Industries", "West"),
                ("XYZ Manufacturing", "North"),
                ("Tech Solutions Ltd", "South"),
                ("Global Motors", "West"),
                ("Precision Engineering", "North"),
                ("AutoParts Co", "East"),
                ("MegaCorp International", "West"),
                ("Local Hardware Store", "South"),
            ]
            
            for name, region in customer_data:
                existing = db.query(Customer).filter(Customer.name == name).first()
                if not existing:
                    db.add(Customer(name=name, region=region))
            commit(db)
            customers = db.query(Customer).all()
        
        # 9️⃣ Create sales orders
        print("📋 Creating sales orders...")
        today = date.today()
        
        if len(customers) >= 5 and len(items) >= 8:
            sales_orders = [
                SalesOrder(customer_id=customers[0].id, order_date=today - timedelta(days=2), promised_date=today + timedelta(days=5), status="OPEN"),
                SalesOrder(customer_id=customers[1].id, order_date=today - timedelta(days=1), promised_date=today + timedelta(days=7), status="OPEN"),
                SalesOrder(customer_id=customers[2].id, order_date=today, promised_date=today + timedelta(days=10), status="OPEN"),
                SalesOrder(customer_id=customers[3].id, order_date=today - timedelta(days=5), promised_date=today + timedelta(days=2), status="PARTIAL"),
                SalesOrder(customer_id=customers[0].id, order_date=today - timedelta(days=25), promised_date=today - timedelta(days=18), status="SHIPPED"),
                SalesOrder(customer_id=customers[1].id, order_date=today - timedelta(days=10), promised_date=today - timedelta(days=3), status="SHIPPED"),
            ]
            db.add_all(sales_orders)
            commit(db)
            
            # Sales order items
            order_items = [
                SalesOrderItem(sales_order_id=sales_orders[0].id, item_id=items[5].id, ordered_qty=50, shipped_qty=0),
                SalesOrderItem(sales_order_id=sales_orders[1].id, item_id=items[6].id, ordered_qty=100, shipped_qty=0),
                SalesOrderItem(sales_order_id=sales_orders[2].id, item_id=items[7].id, ordered_qty=20, shipped_qty=0),
                SalesOrderItem(sales_order_id=sales_orders[3].id, item_id=items[5].id, ordered_qty=60, shipped_qty=40),
                SalesOrderItem(sales_order_id=sales_orders[4].id, item_id=items[5].id, ordered_qty=80, shipped_qty=80),
            ]
            db.add_all(order_items)
            commit(db)
            print(f"   Created {len(sales_orders)} sales orders")
        
        # 🔟 Get or create machines
        print("⚙️ Getting machines...")
        machines = db.query(Machine).all()
        if len(machines) < 3:
            db.add(Machine(machine_code="MC-01", capacity_per_day=100, efficiency=0.95))
            db.add(Machine(machine_code="MC-02", capacity_per_day=150, efficiency=0.90))
            commit(db)
        
        # 1️⃣1️⃣ Get or create roles
        print("👤 Getting roles...")
        roles = db.query(Role).all()
        role_names = [r.name for r in roles]
        
        for role_name in ["ADMIN", "WAREHOUSE_MANAGER", "SALES_MANAGER", "PRODUCTION_PLANNER"]:
            if role_name not in role_names:
                db.add(Role(name=role_name))
        commit(db)
        roles = db.query(Role).all()
        
        # 1️⃣2️⃣ Ensure test user exists
        print("🔐 Ensuring test user exists...")
        DUMMY_USER_ID = UUID("22222222-2222-2222-2222-222222222222")
        
        dummy_user = db.query(AppUser).filter(AppUser.id == DUMMY_USER_ID).first()
        if not dummy_user:
            dummy_user = AppUser(
                id=DUMMY_USER_ID,
                name="Test User",
                role_id=roles[0].id,
                plant_id=plants[0].id
            )
            db.add(dummy_user)
            commit(db)
        
        # 1️⃣3️⃣ Create tasks
        print("📋 Creating tasks...")
        if len(items) >= 3:
            tasks = [
                Task(task_type="REORDER", reference_type="ITEM", reference_id=items[0].id, 
                     reference_name=items[0].name, priority="HIGH", status="OPEN", assigned_to=dummy_user.id),
                Task(task_type="REORDER", reference_type="ITEM", reference_id=items[1].id, 
                     reference_name=items[1].name, priority="HIGH", status="OPEN", assigned_to=dummy_user.id),
                Task(task_type="QUALITY_CHECK", reference_type="ITEM", reference_id=items[2].id, 
                     reference_name=items[2].name, priority="MEDIUM", status="IN_PROGRESS", assigned_to=dummy_user.id),
            ]
            db.add_all(tasks)
            commit(db)
        
        # 1️⃣4️⃣ Ensure contexts exist
        print("🔐 Ensuring data contexts exist...")
        inventory_context = db.query(DataContext).filter(DataContext.name == "Inventory Analytics").first()
        if not inventory_context:
            inventory_context = DataContext(
                name="Inventory Analytics",
                context_type="INVENTORY",
                primary_table="inventory_balance",
                allowed_tables=["inventory_balance", "item", "warehouse", "plant"],
                allowed_columns={
                    "inventory_balance": ["quantity_on_hand", "item_id", "warehouse_id"],
                    "item": ["sku", "name", "item_type", "uom", "reorder_level", "safety_stock"],
                    "warehouse": ["name", "type"],
                    "plant": ["name", "location"]
                },
                allowed_metrics=["total_stock", "below_reorder_level", "stock_by_warehouse"]
            )
            db.add(inventory_context)
            commit(db)
        
        # 1️⃣5️⃣ Ensure test session exists
        print("🔓 Ensuring test session exists...")
        TEST_SESSION_ID = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
        
        test_session = db.query(ContextSession).filter(ContextSession.id == TEST_SESSION_ID).first()
        if not test_session:
            test_session = ContextSession(
                id=TEST_SESSION_ID,
                data_context_id=inventory_context.id,
                user_id=DUMMY_USER_ID
            )
            db.add(test_session)
            commit(db)
        
        print("\n" + "="*70)
        print("✅ Comprehensive seeding completed successfully!")
        print("="*70)
        print(f"\n📊 Data Summary:")
        print(f"   • Organizations: {db.query(Organization).count()}")
        print(f"   • Plants: {db.query(Plant).count()}")
        print(f"   • Warehouses: {db.query(Warehouse).count()}")
        print(f"   • Items: {db.query(Item).count()}")
        print(f"   • Inventory Balances: {db.query(InventoryBalance).count()}")
        print(f"   • Vendors: {db.query(Vendor).count()}")
        print(f"   • Customers: {db.query(Customer).count()}")
        print(f"   • Sales Orders: {db.query(SalesOrder).count()}")
        print(f"   • Tasks: {db.query(Task).count()}")
        print(f"   • Users: {db.query(AppUser).count()}")
        
        print(f"\n🔑 Test Session ID: {TEST_SESSION_ID}")
        print(f"   Use this in your API tests!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    comprehensive_seed()