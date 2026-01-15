from django.contrib.admin.options import InlineModelAdmin

from bis.permissions import Permissions


class PermissionMixin:
    def get_action_choices(self, request):
        return super().get_action_choices(request, [("", "Vyber hromadnou akci zde")])

    def get_queryset(self, request):
        self.request = request
        queryset = super().get_queryset(request)

        if isinstance(self, InlineModelAdmin):
            return queryset

        queryset = Permissions(request.user, self.model, "backend").filter_queryset(
            queryset
        )

        if ordering := self.get_ordering(request):
            queryset = queryset.order_by(*ordering)

        return queryset

    def has_view_permission(self, request, obj=None):
        # individual objects are filtered using get_queryset,
        # this is used only for disabling whole admin model
        return Permissions(request.user, self.model, "backend").has_view_permission(obj)

    def has_add_permission(self, request, obj=None):
        return Permissions(request.user, self.model, "backend").has_add_permission(obj)

    def has_change_permission(self, request, obj=None):
        return Permissions(request.user, self.model, "backend").has_change_permission(
            obj
        )

    def has_delete_permission(self, request, obj=None):
        return Permissions(request.user, self.model, "backend").has_delete_permission(
            obj
        )

    def get_extra(self, request, obj=None, **kwargs):
        if self.has_add_permission(request, obj):
            return super().get_extra(request, obj, **kwargs)

        return 0

    @staticmethod
    def saving_raw(request):
        return request.method == "POST" and "_save_raw" in request.POST

    def set_no_validation_if_raw_saving(self, request, kwargs):
        if self.saving_raw(request):

            class NoValidationForm(self.form):
                def full_clean(_self):
                    super(NoValidationForm, _self).full_clean()
                    _self._errors = {}

            kwargs["form"] = NoValidationForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        self.set_no_validation_if_raw_saving(request, kwargs)
        return super().get_form(request, obj, change, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        self.set_no_validation_if_raw_saving(request, kwargs)
        return super().get_formset(request, obj, **kwargs)


class ReadonlyMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
