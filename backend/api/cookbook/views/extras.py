from rest_framework.decorators import api_view
from rest_framework.response import Response
from translation.translate import model_translations, string_translations


@api_view(["get"])
def translations(request):
    return Response(
        {
            "string_translations": string_translations,
            "model_translations": model_translations,
        }
    )
