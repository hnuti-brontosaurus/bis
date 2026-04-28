import game_book
from django.urls import path

# from game_book.filters import AdministrationUnitAutocomplete
from game_book.views import EditGameView, GameBookView, GameView, NewGameView

urlpatterns = [
    path("", GameBookView.as_view(), name="game_book"),
    path("new_game/", NewGameView.as_view(), name="new_game"),
    path("game/<int:pk>/", GameView.as_view(), name="game"),
    path("game/<int:pk>/edit/", EditGameView.as_view(), name="edit_game"),
    path("game/<int:pk>/toggle/<str:what>/", game_book.views.toggle),
    # path('autocomplete/administration_unit/', AdministrationUnitAutocomplete.as_view(),
    #      name='administration_unit_autocomplete'),
]
