import csv
from sqlmodel import Session
from datetime import datetime

# Import your database engine and V2 models
from src.database import engine
from src.models import (
    Transaction,
    TransactionTypeEnum,
    CategoryEnum,
    StatusEnum,
    UnitOfMeasureEnum,
)


def parse_date(date_string: str):
    """Smart parser that tries multiple formats to prevent spreadsheet crashes."""
    clean_date = date_string.strip()
    try:
        # Try the YYYY-MM-DD format (The one from your error)
        return datetime.strptime(clean_date, "%Y-%m-%d").date()
    except ValueError:
        # Fallback to the MM/DD/YYYY format just in case
        return datetime.strptime(clean_date, "%m/%d/%Y").date()


def get_v2_category(old_category: str) -> CategoryEnum:
    """Safely maps the old spreadsheet categories to the strict V2 Enums."""
    mapping = {
        "Feed": CategoryEnum.feed,
        "Medication": CategoryEnum.medicine,
        "Utilities": CategoryEnum.utilities,
        "Labor": CategoryEnum.labor,
        "Livestock / Fixed Assets.": CategoryEnum.assets,
        "Rent / Property Costs": CategoryEnum.assets,
        "Transportation": CategoryEnum.transport,
    }
    clean_cat = str(old_category).strip()
    return mapping.get(clean_cat, CategoryEnum.other_expense)


def guess_unit_of_measure(category: CategoryEnum) -> UnitOfMeasureEnum:
    """A smart guesser to fill in the missing V2 Unit of Measure column."""
    if category == CategoryEnum.feed:
        return UnitOfMeasureEnum.kg
    elif category == CategoryEnum.labor:
        return UnitOfMeasureEnum.job
    elif category == CategoryEnum.assets:
        return UnitOfMeasureEnum.job
    else:
        return UnitOfMeasureEnum.other


def run_migration():
    print("🚀 Starting V2 Data Migration (Vanilla Python Mode)...")

    with Session(engine) as session:
        success_count = 0

        try:
            with open("data.csv", mode="r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                print(f"📊 Found {len(rows)} records in data.csv")

                for index, row in enumerate(rows):
                    try:
                        # --- Map the Old Data using the Smart Date Parser ---
                        date_obj = parse_date(row["Date"])
                        old_category_str = row["Category"]
                        item_desc = str(row["Item_Description"]).strip()
                        qty = float(row["Qty"])
                        unit_price = float(row["Unit_Price"])
                        total_amount = float(row["Total_Amount"])

                        # --- The V2 Upgrades & Smart Defaults ---
                        v2_category = get_v2_category(old_category_str)
                        v2_uom = guess_unit_of_measure(v2_category)

                        v2_amount_paid = total_amount
                        v2_status = StatusEnum.paid

                        # Create the V2 Transaction Record
                        new_txn = Transaction(
                            txn_date=date_obj,
                            txn_type=TransactionTypeEnum.expense,
                            category=v2_category,
                            item_description=item_desc,
                            qty=qty,
                            unit_of_measure=v2_uom,
                            unit_price=unit_price,
                            total_amount=total_amount,
                            amount_paid=v2_amount_paid,
                            payment_status=v2_status,
                            entity_name=None,
                            reference_tag=None,
                            remarks="Legacy CSV Import",
                        )

                        session.add(new_txn)
                        success_count += 1

                    except Exception as e:
                        print(f"⚠️ Skipping row {index + 2} due to data error: {e}")

        except FileNotFoundError:
            print("❌ Error: data.csv not found in this directory.")
            return

        print("💾 Committing to the PostgreSQL vault...")
        session.commit()
        print(
            f"✅ Migration Complete! Successfully imported {success_count} V2 transactions."
        )


if __name__ == "__main__":
    run_migration()
