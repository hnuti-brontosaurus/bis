import json
from pathlib import Path

from bis.models import User
from django.core.management.base import BaseCommand
from ecomail.helpers import send
from xlsx_export.export import XLSXWriter
from xlsx_export.serializers import UserExportSerializer


class Command(BaseCommand):
    status = {
        1: "subscribed",
        2: "unsubscribed",
        3: "soft bounce",
        4: "hard bounce",
        5: "spam complaint",
        6: "unconfirmed",
    }

    def get_subscribers(self):
        data = []
        page = 0
        while True:
            page += 1

            print(page)
            result = send([], "GET", "lists/28/subscribers", params=dict(page=page))
            print(result)
            data += result["data"]
            if not result["next_page_url"]:
                break

        return data

    def handle(self, *args, **options):
        path = Path("data.json")

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = self.get_subscribers()

            with open(path, "w", encoding="ut-8") as f:
                json.dump(data, f)

        bis_emails = set(User.objects.values_list("email", flat=True))
        data_emails = [u for u in data if "+" not in u["email"]]
        data_emails = [u for u in data_emails if u["status"] == 1]
        data_emails = set([u["email"] for u in data_emails])
        print(
            len(bis_emails),
            len(data_emails),
            len(bis_emails.intersection(data_emails)),
            len(bis_emails - data_emails),
            len(data_emails - bis_emails),
        )
        #
        # q = []
        # for item in data:
        #     if item['email'] in (data_emails - bis_emails):
        #         q.append({
        #             'email': item['email'],
        #             'subscribed_at': item['subscribed_at'],
        #             'name': item['subscriber']['name'],
        #             'surname': item['subscriber']['surname'],
        #             'source': item['subscriber']['source'],
        #         })
        #
        # with open('ecomail_only.txt', 'w', encoding='utf-8') as f2:
        #     json.dump(q, f2, indent=2, ensure_ascii=False)
        #
        # users = User.objects.filter(email__in=bis_emails - data_emails)
        #
        # users = UserExportSerializer.get_related(users)
        #
        # writer = XLSXWriter(users.model._meta.verbose_name_plural)
        # writer.from_queryset(users, UserExportSerializer)
        # file = writer.get_file()
        # with open(file.name, 'rb') as f1:
        #     with open('bis_only.xlsx', 'wb') as f2:
        #         f2.write(f1.read())
        #
        # # print(json.dumps(data[0], indent=2))
