import pytest
from bis.tests.test_mcp_visibility import make_event
from common import sensitivity
from common.sensitivity import Sensitivity, classify_unclassified
from event.models import EventRegistration
from questionnaire.models import Question, Questionnaire


@pytest.fixture
def questionnaire(db):
    registration = EventRegistration.objects.create(event=make_event("Akce"))
    return Questionnaire.objects.create(event_registration=registration)


def make_question(questionnaire, text, sensitivity=None):
    question = Question.objects.create(questionnaire=questionnaire, question=text)
    if sensitivity:
        Question.objects.filter(id=question.id).update(sensitivity=sensitivity)
        question.refresh_from_db()
    return question


def test_new_question_reuses_an_identical_classification(questionnaire):
    make_question(questionnaire, "Alergie?", Sensitivity.HEALTH)

    assert make_question(questionnaire, "Alergie?").sensitivity == Sensitivity.HEALTH
    assert make_question(questionnaire, "Odkud jedeš?").sensitivity is None


def test_only_a_changed_question_loses_its_classification(questionnaire):
    question = make_question(questionnaire, "Odkud jedeš?", Sensitivity.NONE)

    question.is_required = False
    question.save()
    assert question.sensitivity == Sensitivity.NONE

    question.question = "Jaké máš léky?"
    question.save()
    assert question.sensitivity is None


def test_classifies_each_distinct_question_once(questionnaire, settings, monkeypatch):
    settings.GROQ_API_KEY = "key"
    asked = []

    def classify(questions, max_retries):
        asked.extend(text for text, _ in questions)
        return [
            Sensitivity.HEALTH if text == "Alergie?" else Sensitivity.NONE
            for text, _ in questions
        ]

    monkeypatch.setattr(sensitivity, "classify", classify)
    for text in ["Alergie?", "Alergie?", "Odkud jedeš?"]:
        make_question(questionnaire, text)
    make_question(questionnaire, "Tričko?", Sensitivity.PERSONAL)

    classify_unclassified(Question, "question")

    assert sorted(asked) == ["Alergie?", "Odkud jedeš?"]
    assert dict(Question.objects.values_list("question", "sensitivity").distinct()) == {
        "Alergie?": Sensitivity.HEALTH,
        "Odkud jedeš?": Sensitivity.NONE,
        "Tričko?": Sensitivity.PERSONAL,
    }
