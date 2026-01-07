from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import (
    Organization, Plant, Warehouse,
    Item, Vendor, VendorItem,
    InventoryTransaction, InventoryBalance,
    Customer, SalesOrder, SalesOrderItem,
    Machine, ProductionPlan, ProductionOrder,
    Role, AppUser, Task
)

# -----------------------------
# Helper
# -----------------------------
def commit(db: Session):
    db.commit()

# -----------------------------
# Seed function
# -----------------------------
def seed():
    db = SessionLocal()

    try:
        # 1️⃣ Organization
        org = Organization(name="Demo Manufacturing Ltd", industry="Manufacturing")
        db.add(org)
        commit(db)

        # 2️⃣ Plants
        plant1 = Plant(
            organization_id=org.id,
            name="Plant A",
            location="Pune",
            timezone="Asia/Kolkata"
        )
        plant2 = Plant(
            organization_id=org.id,
            name="Plant B",
            location="Nagpur",
            timezone="Asia/Kolkata"
        )
        db.add_all([plant1, plant2])
        commit(db)

        # 3️⃣ Warehouses
        wh_raw = Warehouse(plant_id=plant1.id, name="RAW Store", type="RAW")
        wh_wip = Warehouse(plant_id=plant1.id, name="WIP Store", type="WIP")
        wh_fg = Warehouse(plant_id=plant1.id, name="FG Store", type="FINISHED")
        db.add_all([wh_raw, wh_wip, wh_fg])
        commit(db)

        # 4️⃣ Items
        raw_items = [
            Item(sku="RM-001", name="Steel Rod", item_type="RAW", uom="KG", reorder_level=500, safety_stock=200),
            Item(sku="RM-002", name="Plastic Granules", item_type="RAW", uom="KG", reorder_level=300, safety_stock=100),
        ]

        fg_items = [
            Item(sku="FG-001", name="Gear Assembly", item_type="FINISHED", uom="PCS"),
            Item(sku="FG-002", name="Motor Housing", item_type="FINISHED", uom="PCS"),
        ]

        db.add_all(raw_items + fg_items)
        commit(db)

        # 5️⃣ Vendors
        vendors = [
            Vendor(name="SteelCorp", location="Mumbai", rating=4.5, lead_time_days=5),
            Vendor(name="PolyPlast", location="Delhi", rating=4.2, lead_time_days=7),
        ]
        db.add_all(vendors)
        commit(db)

        # 6️⃣ Vendor Item Pricing
        vendor_items = [
            VendorItem(vendor_id=vendors[0].id, item_id=raw_items[0].id, unit_price=55),
            VendorItem(vendor_id=vendors[1].id, item_id=raw_items[1].id, unit_price=40),
        ]
        db.add_all(vendor_items)
        commit(db)

        # 7️⃣ Inventory Transactions (IN)
        transactions = [
            InventoryTransaction(
                item_id=raw_items[0].id,
                warehouse_id=wh_raw.id,
                transaction_type="IN",
                quantity=1000,
                reference_type="PO"
            ),
            InventoryTransaction(
                item_id=raw_items[1].id,
                warehouse_id=wh_raw.id,
                transaction_type="IN",
                quantity=800,
                reference_type="PO"
            )
        ]
        db.add_all(transactions)
        commit(db)

        # 8️⃣ Inventory Balance (derived)
        balances = [
            InventoryBalance(item_id=raw_items[0].id, warehouse_id=wh_raw.id, quantity_on_hand=1000),
            InventoryBalance(item_id=raw_items[1].id, warehouse_id=wh_raw.id, quantity_on_hand=800),
        ]
        db.add_all(balances)
        commit(db)

        # 9️⃣ Customers
        customer = Customer(name="ABC Industries", region="West")
        db.add(customer)
        commit(db)

        # 🔟 Sales Order
        so = SalesOrder(
            customer_id=customer.id,
            order_date=date.today(),
            promised_date=date.today() + timedelta(days=7),
            status="OPEN"
        )
        db.add(so)
        commit(db)

        so_item = SalesOrderItem(
            sales_order_id=so.id,
            item_id=fg_items[0].id,
            ordered_qty=50,
            shipped_qty=0
        )
        db.add(so_item)
        commit(db)

        # 1️⃣1️⃣ Machine
        machine = Machine(machine_code="MC-01", capacity_per_day=100, efficiency=0.9)
        db.add(machine)
        commit(db)

        # 1️⃣2️⃣ Production Plan
        plan = ProductionPlan(
            item_id=fg_items[0].id,
            planned_qty=100,
            planned_date=date.today()
        )
        db.add(plan)
        commit(db)

        # 1️⃣3️⃣ Production Order
        prod_order = ProductionOrder(
            item_id=fg_items[0].id,
            machine_id=machine.id,
            planned_qty=100,
            actual_qty=90,
            status="COMPLETED"
        )
        db.add(prod_order)
        commit(db)

        # 1️⃣4️⃣ Roles & Users
        admin_role = Role(name="ADMIN")
        planner_role = Role(name="PLANNER")
        db.add_all([admin_role, planner_role])
        commit(db)

        user = AppUser(name="Operations Manager", role_id=admin_role.id, plant_id=plant1.id)
        db.add(user)
        commit(db)

        # 1️⃣5️⃣ Task
        task = Task(
            task_type="REORDER",
            reference_type="ITEM",
            reference_id=raw_items[0].id,
            priority="HIGH",
            status="OPEN",
            assigned_to=user.id
        )
        db.add(task)
        commit(db)

        print("✅ Dummy data seeded successfully")

    except Exception as e:
        db.rollback()
        print("❌ Seeding failed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed()
