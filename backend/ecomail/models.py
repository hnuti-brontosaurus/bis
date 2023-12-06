from django.db import models


class Contact(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['id']
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakty"


class ContactLog(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()
    log = models.TextField()

    class Meta:
        ordering = ['id']
        verbose_name = "Záznam aktivity kontaktu"
        verbose_name_plural = "Záznamy aktivity kontaktu"

    def __str__(self):
        return f"{self.created}"
