import csv
from io import StringIO

from categories.models import DonationSourceCategory
from django.utils.datetime_safe import date
from donations.models import Donation, Donor


def upload_bank_records(file):
    assert file.name.endswith(".csv"), "Soubor není ve formátu .csv"

    column_names = [
        "Datum",
        "Objem",
        "Měna",
        "Číslo účtu",
        "Protiúčet",
        "Kód banky",
        "KS",
        "VS",
        "SS",
        "Poznámka",
        "Zpráva pro příjemce",
        "Typ",
        "Upřesnění - objem",
        "Upřesnění - měna",
        "VS",
    ]

    data = StringIO(file.read().decode("utf-8").strip())
    data = list(csv.reader(data, delimiter=";"))
    header, data = data[0], data[1:]

    for i, column in enumerate(column_names):
        assert column in header[i], f"{i+1}. sloupec není {column}"

    source = DonationSourceCategory.objects.get(slug="bank_transfer")
    for row in data:
        day, month, year = row[0].split(".")
        variable_symbol = row[7] or None
        donor = Donor.objects.filter(
            variable_symbols__variable_symbol=variable_symbol
        ).first()
        Donation.objects.get_or_create(
            donor=donor,
            donated_at=date(int(year), int(month), int(day)),
            amount=round(float(row[1].replace(",", "."))),
            donation_source=source,
            _variable_symbol=variable_symbol,
            info="\n".join(
                [f"{column_names[i]}: {row[i]}" for i in range(len(column_names))]
            ),
        )
