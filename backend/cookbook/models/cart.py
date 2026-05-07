from bis.models import User
from cookbook.models.base import BaseModel
from django.db import models as m
from django.db.models import CASCADE


class Cart(BaseModel):
    user = m.OneToOneField(User, related_name="cart", on_delete=CASCADE)
    items = m.JSONField(default=list)
    updated_at = m.DateTimeField(auto_now=True)
