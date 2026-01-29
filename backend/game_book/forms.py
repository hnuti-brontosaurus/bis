from django import forms
from django.forms import Form, ModelForm, TextInput
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from administration_units.models import AdministrationUnit
from bis.models import User
from game_book.models import Comment, Game
from game_book_categories.models import (
    GameLengthCategory,
    LocationCategory,
    MaterialRequirementCategory,
    MentalCategory,
    OrganizersNumberCategory,
    ParticipantAgeCategory,
    ParticipantNumberCategory,
    PhysicalCategory,
    PreparationLengthCategory,
    Tag,
)
from translation.translate import _


class CategoryChoiceMixin:
    def label_from_instance(self, obj):
        if obj.description:
            return mark_safe(
                f'<span data-bs-toggle="tooltip" data-bs-title="{obj.description}">{obj}</span>'
            )
        return str(obj)


class CategoryChoiceField(CategoryChoiceMixin, forms.ModelChoiceField):
    pass


class CategoryMultipleChoiceField(CategoryChoiceMixin, forms.ModelMultipleChoiceField):
    pass


class FilterForm(Form):
    search_input = forms.CharField(label="Hledej v textu", required=False)
    order = forms.ChoiceField(
        label="Pořadí",
        required=False,
        choices=(
            ("-created_at", "Nejnovější"),
            ("thumbs_up", "Nejpopulárnější"),
            ("favourites", "Nejoblíbenější"),
        ),
    )

    only_my_games = forms.BooleanField(label="Jen mé programy", required=False)
    only_my_favourites = forms.BooleanField(
        label="Jen mé oblíbené programy", required=False
    )
    only_watched_by_me = forms.BooleanField(
        label="Jen mnou sledované programy", required=False
    )
    is_original = forms.BooleanField(
        label="Jen autorské (originální) programy", required=False
    )
    is_verified = forms.BooleanField(label="Jen ověřené programy", required=False)

    created_at__gte = forms.DateField(
        label="Vytvořeno po datu",
        required=False,
        widget=TextInput(attrs={"type": "date"}),
    )
    created_at__lte = forms.DateField(
        label="Vytvořeno před datem",
        required=False,
        widget=TextInput(attrs={"type": "date"}),
    )
    contributor = forms.ModelChoiceField(
        label=_("models.Game.fields.contributor"),
        queryset=User.objects.exclude(games=None),
        required=False,
    )
    administration_unit = forms.ModelChoiceField(
        label=_("models.Game.fields.administration_unit"),
        queryset=AdministrationUnit.objects.all(),
        required=False,
    )
    tags = CategoryMultipleChoiceField(
        label=_("models.Game.fields.tags"),
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    physical_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.physical_category"),
        queryset=PhysicalCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    mental_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.mental_category"),
        queryset=MentalCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    location_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.location_category"),
        queryset=LocationCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    participant_number_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.participant_number_category"),
        queryset=ParticipantNumberCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    participant_age_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.participant_age_category"),
        queryset=ParticipantAgeCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    game_length_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.game_length_category"),
        queryset=GameLengthCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    preparation_length_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.preparation_length_category"),
        queryset=PreparationLengthCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    material_requirement_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.material_requirement_category"),
        queryset=MaterialRequirementCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    organizers_number_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.organizers_number_category"),
        queryset=OrganizersNumberCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )


class GameForm(ModelForm):
    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None,
    ):
        super().__init__(
            data,
            files,
            auto_id,
            prefix,
            initial,
            error_class,
            label_suffix,
            empty_permitted,
            instance,
            use_required_attribute,
            renderer,
        )
        if not self.instance.contributor_id:
            self.fields.pop("contributor")
        else:
            self.fields["contributor"].choices = [
                (self.instance.contributor.id, self.instance.contributor)
            ]
            self.fields["contributor"].disabled = True

    tags = CategoryMultipleChoiceField(
        label=_("models.Game.fields.tags"),
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    physical_category = CategoryChoiceField(
        label=_("models.Game.fields.physical_category"),
        queryset=PhysicalCategory.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
    )
    mental_category = CategoryChoiceField(
        label=_("models.Game.fields.mental_category"),
        queryset=MentalCategory.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
    )
    location_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.location_category"),
        queryset=LocationCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
    )
    participant_number_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.participant_number_category"),
        queryset=ParticipantNumberCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
    )
    participant_age_category = CategoryMultipleChoiceField(
        label=_("models.Game.fields.participant_age_category"),
        queryset=ParticipantAgeCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
    )
    game_length_category = CategoryChoiceField(
        label=_("models.Game.fields.game_length_category"),
        queryset=GameLengthCategory.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
    )
    preparation_length_category = CategoryChoiceField(
        label=_("models.Game.fields.preparation_length_category"),
        queryset=PreparationLengthCategory.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
    )
    material_requirement_category = CategoryChoiceField(
        label=_("models.Game.fields.material_requirement_category"),
        queryset=MaterialRequirementCategory.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
    )
    organizers_number_category = CategoryChoiceField(
        label=_("models.Game.fields.organizers_number_category"),
        queryset=OrganizersNumberCategory.objects.all(),
        widget=forms.RadioSelect(),
        required=True,
    )

    class Meta:
        model = Game
        fields = [
            "name",
            "contributor",
            "is_original",
            "origin",
            "administration_unit",
            "is_hidden",
            "is_verified",
            "tags",
            "physical_category",
            "physical_note",
            "mental_category",
            "mental_note",
            "location_category",
            "location_note",
            "participant_number_category",
            "participant_number_note",
            "participant_age_category",
            "participant_age_note",
            "game_length_category",
            "game_length_note",
            "preparation_length_category",
            "preparation_length_note",
            "material_requirement_category",
            "material_requirement_note",
            "organizers_number_category",
            "organizers_number_note",
            "goal",
            "short_description",
            "motivation",
            "description",
            "material",
            "notes",
        ]
        widgets = {
            "is_hidden": forms.CheckboxInput(attrs={"disabled": True}),
            "is_verified": forms.CheckboxInput(attrs={"disabled": True}),
            "tags": forms.CheckboxSelectMultiple(),
            "origin": forms.Textarea(attrs={"rows": 2}),
            "physical_note": forms.Textarea(attrs={"rows": 2}),
            "mental_note": forms.Textarea(attrs={"rows": 2}),
            "location_note": forms.Textarea(attrs={"rows": 2}),
            "participant_number_note": forms.Textarea(attrs={"rows": 2}),
            "participant_age_note": forms.Textarea(attrs={"rows": 2}),
            "game_length_note": forms.Textarea(attrs={"rows": 2}),
            "preparation_length_note": forms.Textarea(attrs={"rows": 2}),
            "organizers_number_note": forms.Textarea(attrs={"rows": 2}),
            "material_requirement_note": forms.Textarea(attrs={"rows": 2}),
            "short_description": forms.Textarea(attrs={"rows": 2}),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            "comment",
        ]
