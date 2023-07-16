from collections import Counter
from copy import copy
from itertools import zip_longest
from os.path import join
from typing import OrderedDict

import openpyxl
import pdfkit
import xlsxwriter
from django.contrib import admin
from django.core.files.temp import NamedTemporaryFile
from django.core.paginator import Paginator
from django.http import FileResponse
from rest_framework.serializers import ModelSerializer
from xlsx2html import xlsx2html

from bis.helpers import print_progress
from bis.models import User
from event.models import Event
from project.settings import BASE_DIR
from xlsx_export.serializers import UserExportSerializer, EventExportSerializer, DonorExportSerializer, \
    DonationExportSerializer, AdministrationUnitExportSerializer


class XLSXWriter:
    def __init__(self, file_name):
        self.tmp_file = NamedTemporaryFile(mode='w', suffix='.xlsx', newline='', encoding='utf8',
                                           prefix=file_name + '_')
        self.writer = xlsxwriter.Workbook(self.tmp_file.name, {'constant_memory': True})

        self.format = lambda: None
        self.format.green = self.writer.add_format({'bg_color': '#c9ffc9'})
        self.format.red = self.writer.add_format({'bg_color': '#ff9999'})
        self.format.shrink = self.writer.add_format()
        self.format.shrink.set_shrink()
        self.format.text_wrap = self.writer.add_format()
        self.format.text_wrap.set_text_wrap()

    def get_file(self):
        self.writer.close()
        self.tmp_file.flush()

        return self.tmp_file

    def add_worksheet(self, name):
        self.worksheet = self.writer.add_worksheet(name)
        self.row = 0
        self.header_keys = []

    def from_queryset(self, queryset, serializer_class):
        self.add_worksheet(queryset.model._meta.verbose_name_plural)

        for page in Paginator(queryset, 100):
            print_progress('exporting xlsx', page.number, page.paginator.num_pages)
            serializer = serializer_class(page.object_list, many=True)
            for item in serializer.data:
                if not self.row:
                    self.write_header(serializer.child.get_fields())
                self.write_row(item)

    def write_values(self, values):
        values = {key: value for key, value in values}
        for i, key in enumerate(self.header_keys):
            value = values.get(key)
            if isinstance(value, list):
                value = '\n'.join(str(v) for v in value)
            if value is False:
                value = 'ne'
            if value is True:
                value = 'ano'
            if value is None:
                value = '-'
            self.worksheet.write(self.row, i, str(value), self.format.shrink)

        self.row += 1

    def get_header_values(self, fields, prefix='', key_prefix=''):
        if prefix: prefix += ' - '
        if key_prefix: key_prefix += '_'
        for key, value in fields.items():
            if isinstance(value, ModelSerializer):
                yield from self.get_header_values(value.get_fields(), prefix + value.Meta.model._meta.verbose_name,
                                                  key_prefix + key)
            else:
                self.header_keys.append(key_prefix + key)
                yield key_prefix + key, prefix + (getattr(value, 'label', value) or key)

    def write_header(self, fields):
        self.write_values(list(self.get_header_values(fields)))

    def get_row_values(self, item, key_prefix=''):
        if key_prefix: key_prefix += '_'
        for key, value in item.items():
            if isinstance(value, OrderedDict):
                yield from self.get_row_values(value, key_prefix + key)
            else:
                yield key_prefix + key, value

    def write_row(self, item):
        self.write_values(self.get_row_values(item))

    def events_stats(self, queryset):
        self.add_worksheet('Uživatelé akcí')
        participants = User.objects.filter(participated_in_events__event__in=queryset)
        organizers = User.objects.filter(events_where_was_organizer__in=queryset)
        main_organizers = User.objects.filter(events_where_was_as_main_organizer__in=queryset)

        self.write_header(dict(
            p='=Učastníci',
            pe='Emaily',
            pc='Počet účastí',
            o='Orgové',
            oe='Emaily orgů',
            oc='Počet zorganizovaných akcí',
            m='Hlavní orgové',
            me='Emaily hlavních orgů',
            mc='Počet odvedených akcí'
        ))

        for line in zip_longest(
                *zip(*Counter(participants).most_common()),
                *zip(*Counter(organizers).most_common()),
                *zip(*Counter(main_organizers).most_common()),
                fillvalue=''
        ):
            row = []
            for item in line:
                if isinstance(item, User):
                    row += [item.get_name(), item.email or '']
                else:
                    row += [item]

            row = {a: b for a, b in zip(self.header_keys, row)}
            self.write_row(row)


@admin.action(description='Exportuj data')
def export_to_xlsx(model_admin, request, queryset):
    serializer_class = \
        [s for s in [UserExportSerializer, EventExportSerializer, DonorExportSerializer, DonationExportSerializer, AdministrationUnitExportSerializer]
         if s.Meta.model is queryset.model][0]
    queryset = serializer_class.get_related(queryset)

    writer = XLSXWriter(queryset.model._meta.verbose_name_plural)
    writer.from_queryset(queryset, serializer_class)
    if queryset.model is Event:
        writer.events_stats(queryset)
    file = writer.get_file()

    return FileResponse(open(file.name, 'rb'))


def get_attendance_list_data(event):
    organizers = list(event.other_organizers.all())
    applications = (registration := getattr(event, "registration", [])) and list(registration.applications.all())
    for item in (organizers + applications):
        address = getattr(item, 'address', None)
        if not address and (applications_user := getattr(item, 'user', None)):
            address = getattr(applications_user, 'address', None)
        yield (
            item.first_name + ' ' + item.last_name,
            item.birthday and item.birthday.strftime("%d. %m. %Y"),
            address and f"{address.street}, {address.city}",
            address and address.zip_code,
            item.email,
            str(item.phone),
        )

    for i in range(max(10, len(applications) // 10)):
        yield 6 * ('',)


def get_attendance_list_rows(ws):
    for i in range(13):
        yield i + 17

    for i in range(25):
        yield i + 31

    start_i = 39
    start = 30
    rows = 26
    while True:
        for i in range(rows):
            source_row = start + i
            row = start + rows + i
            ws.row_dimensions[row] = copy(ws.row_dimensions[source_row])
            for col in "ABSCDEFGH":
                ws[f"{col}{row}"] = None
                ws[f"{col}{row}"]._style = copy(ws[f"{col}{source_row}"]._style)

            if i != 0:
                ws[f"A{row}"] = start_i
                start_i += 1

        start += rows

        for i in range(25):
            yield start + 1 + i


def get_attendance_list(event: Event):
    wb = openpyxl.load_workbook(join(BASE_DIR, "xlsx_export", "fixtures", "attendance_list_template.xlsx"))
    ws = wb.active

    ws['C2'] = 5 * event.name
    ws['C3'] = event.get_date()
    ws['C4'] = event.location.name
    ws['C5'] = ", ".join(au.abbreviation for au in event.administration_units.all())

    for row, data in zip(get_attendance_list_rows(ws), get_attendance_list_data(event)):
        for cell, value in zip("BCDEFG", data):
            ws[f"{cell}{row}"] = value

    tmp_xlsx = NamedTemporaryFile(mode='w', suffix='.xlsx', newline='', encoding='utf8',
                                  prefix='attendance_list_')
    tmp_html = NamedTemporaryFile(mode='w', suffix='.html', newline='', encoding='utf8',
                                  prefix='attendance_list_')
    tmp_pdf = NamedTemporaryFile(mode='w', suffix='.pdf', newline='', encoding='utf8',
                                 prefix='attendance_list_')

    wb.save(tmp_xlsx.name)

    xlsx2html(tmp_xlsx.name, tmp_html.name)

    pdfkit.from_file(tmp_html.name, tmp_pdf.name, {
        'page-size': "A4",
        'encoding': "UTF-8",
        'orientation': 'Landscape',
        'title': 'Landscape',
    })

    return {
        'xlsx': FileResponse(open(tmp_xlsx.name, 'rb')),
        'pdf': FileResponse(open(tmp_pdf.name, 'rb'))
    }
