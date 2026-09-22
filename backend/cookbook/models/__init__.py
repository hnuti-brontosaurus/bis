# Django imports only this package, so a model module left out here stays
# invisible to the app registry until some other module happens to import it,
# and migrate plans to delete its tables in the meantime.
from cookbook.models import cart, chefs, ingredients, menus, recipes  # noqa: F401
