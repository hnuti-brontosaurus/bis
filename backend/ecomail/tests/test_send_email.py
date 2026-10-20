import pytest
from ecomail import ecomail

SENDER = ("BIS", "bis@brontosaurus.cz")


@pytest.fixture
def requests(db, monkeypatch, settings):
    settings.ENVIRONMENT = "prod"
    responses = []
    sent = []

    def send(contacts, method, uri, data):
        sent.append([recipient["email"] for recipient in data["message"]["to"]])
        return responses.pop(0)

    monkeypatch.setattr(ecomail, "send", send)
    return responses, sent


def accepted(count):
    return {"results": {"total_accepted_recipients": count}}


def test_refused_recipient_is_dropped_and_the_rest_resent(requests):
    responses, sent = requests
    responses += [
        {"errors": {"message.to.1.email": ["Invalid email address."]}},
        accepted(2),
    ]

    ecomail.send_email(
        SENDER, 1, ["a@example.com", "b@gmail.cz", "c@example.com"], subject="Hi"
    )

    assert sent[1] == ["a@example.com", "c@example.com"]


def test_only_recipient_refused_sends_nothing_more(requests):
    responses, sent = requests
    responses += [{"errors": {"message.to.0.email": ["Invalid email address."]}}]

    ecomail.send_email(SENDER, 1, ["b@gmail.cz"], subject="Hi")

    assert len(sent) == 1


def test_other_validation_error_raises(requests):
    responses, _sent = requests
    responses += [
        {
            "errors": {
                "message.to.0.email": ["Invalid email address."],
                "message.template_id": ["Not found."],
            }
        }
    ]

    with pytest.raises(RuntimeError):
        ecomail.send_email(SENDER, 1, ["b@gmail.cz"], subject="Hi")
