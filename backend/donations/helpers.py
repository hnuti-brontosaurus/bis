import csv
from datetime import date
from io import StringIO

from categories.models import DonationSourceCategory
from donations.models import Donation, Donor


def upload_bank_records(file):
    assert file.name.endswith(".csv"), "Soubor není ve formátu .csv"

    required_columns = [
        "Datum",
        "Objem",
        "VS",
    ]

    data = StringIO(file.read().decode("utf-8-sig").strip())
    data = list(csv.reader(data, delimiter=";"))
    header, data = data[0], data[1:]

    header = {i: column.strip() for i, column in enumerate(header)}
    for column in required_columns:
        assert column in header.values(), f"Sloupec {column} není přítomen"

    source = DonationSourceCategory.objects.get(slug="bank_transfer")
    for row in data:
        row = {header[i]: row[i] for i in range(len(row))}
        day, month, year = row["Datum"].split(".")
        variable_symbol = row["VS"] or None
        donor = None
        if variable_symbol:
            donor = Donor.objects.filter(
                variable_symbols__variable_symbol=variable_symbol
            ).first()
        Donation.objects.get_or_create(
            donor=donor,
            donated_at=date(int(year), int(month), int(day)),
            amount=round(float(row["Objem"].replace(",", "."))),
            donation_source=source,
            _variable_symbol=variable_symbol,
            info="\n".join([f"{key}: {value}" for key, value in row.items()]),
        )
