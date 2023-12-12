from administration_units.models import AdministrationUnit
from dal import autocomplete
from django_bootstrap5.renderers import FieldRenderer
from game_book.models import Game


class GameBookFieldRenderer(FieldRenderer):
    def get_server_side_validation_classes(self):
        if not hasattr(self.field.form, "hide_validation_classes"):
            return super().get_server_side_validation_classes()
        return ""


#
# class AdministrationUnitAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         queryset = AdministrationUnit.objects.all()
#
#         if self.q:
#             queryset = queryset.filter(name__icontains=self.q)
#
#         return queryset
