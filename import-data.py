import pandas as pd
from sqlmodel import Session
from src.database import engine
from src.models import Transaction


def run_import():
    print("Reading CSV...")
    # 1. Read the exact original file you uploaded
    df = pd.read_csv("data.csv")

    # 2. Clean the data (converts all blank spaces and NaNs to empty strings)
    df = df.fillna("")

    print(f"Found {len(df)} records. Beginning import...")

    # 3. Your updated Translation Dictionary
    category_map = {
        "Livestock / Fixed Assets.": "Property",
        "Rent / Property Costs": "Rent",
        "Medication": "Medicine",
        "Transport": "Transport",  # <-- Now officially mapped!
        "Labor": "Labor",
        "Utilities": "Utilities",
        "Feed": "Feed",
    }

    # 4. Open the vault
    with Session(engine) as session:
        for index, row in df.iterrows():
            # Lookup category, default to "Other" if it's completely unrecognized
            safe_category = category_map.get(row["Category"], "Other")

            # Python Logic: If the 'Type' cell was empty in the CSV, force it to be "Expense"
            txn_type = row["Type"] if row["Type"] != "" else "Expense"

            # Python Logic: Translate Google Sheets "Full/Part" to your strict Enums
            status = "Paid" if row["Payment_Status"] == "Full" else "Partially Paid"

            # Map the spreadsheet rows to your strict Python blueprint
            new_txn = Transaction(
                txn_date=row["Date"],
                txn_type=txn_type,
                category=safe_category,
                item_description=row["Item_Description"],
                qty=row["Qty"],
                unit_price=row["Unit_Price"],
                total_amount=row["Total_Amount"],
                payment_status=status,
                remarks=row["Remarks"] if row["Remarks"] != "" else None,
            )
            session.add(new_txn)

        # 5. Commit all records at once
        session.commit()
        print("Import Complete! All data saved to PostgreSQL.")


if __name__ == "__main__":
    run_import()
