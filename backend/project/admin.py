from django.contrib import admin
from django.utils.safestring import mark_safe

from translation.translate import _


class MyAdminSite(admin.AdminSite):
    site_title = 'BIS'
    site_header = mark_safe(f'<img src="/backend_static/logo/br_white_right.png" '
                            f'style="height: 60px; margin: -5px 0px -5px -35px">{_("admin.header")}</img>')
    index_title = _('admin.subheader')
    empty_value_display = 'Nevyplněno'

    def get_app_list(self, request):
        list = super().get_app_list(request)

        order = [
            'administration_units',
            'bis',
            'opportunities',
            'donations',
            'game_book',
            'other',
            'categories',
            'regions',
            'game_book_categories',
        ]
        list.sort(key=lambda value: order.index(value['app_label']))
        return list
