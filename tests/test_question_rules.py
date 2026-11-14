"""11 Nov 2026: the final question rules decided by Mohnish Grover (QUESTION_RULES=on).
1. Daniel's data-location rule restored (Q22, Q23, Q24), even with the narrowed rules on. Backup-replication
   questions (Q24) go to a person like every other data-location question (13 Nov).
2. Q20 (export missing records created before the job) and Q11 (automated jobs failing after a password change) go
   to a person: no article answers them.
Q21 and Q27 stay automatic, and the billing narrowing is unchanged. Texts are the customers' own words."""
import pytest

from src import safety

DATA_LOCATION = [
    "One of our customers has asked for written confirmation of where their data is physically stored.",       # Q22
    "We need our data to remain within the EU for a contract we are signing.",                                  # Q23
    "Where is our data hosted?",
    # backup questions that also ask for something, or raise a security concern: still a person
    "Our backups must stay in the EU. Can you confirm in writing that they are not copied to another region?",
    "Please move our organisation and its backups to the Frankfurt region.",
    "Can you delete all backups stored outside Europe?",
    "Stop copying our backups to another region please.",
    "Our backups were copied to another region without permission, someone accessed them.",
]
# Q24, backup replication: to a person like every other data-location question (13 Nov). Includes rewordings the
# development tickets do not contain.
BACKUP_QUESTIONS = [
    "Are backups replicated outside our primary region? A compliance review has raised this and I need a definite answer.",
    "are backups replicated outside our primary region? please help fast.",
    "Do you copy our backups to another region?",
    "where are our backups kept? same region as the data or somewhere else?",
    "backup is going to other region or not? we need to know for audit team",
    "Is cross-region replication of backups switched on by default?",
]
Q20 = ["Our export is missing records that were definitely created before I started the job.",
       "our export missing records definitely created before I start job. sorry for my english."]
STAY_AUTOMATIC = [
    "I started an export late last night and it is still showing as queued. Should I cancel and try again?",  # Q21
    "There are charges on our invoice for a service I do not believe we use. Could you explain?",              # Q14
    "The download link from our export has expired. Is the file still available?",                             # Q19
]


@pytest.fixture
def final_rules(monkeypatch):
    monkeypatch.setenv("NARROW_RULES", "on")
    monkeypatch.setenv("QUESTION_RULES", "on")


@pytest.mark.parametrize("text", DATA_LOCATION)
def test_every_data_location_question_goes_to_a_person(final_rules, text):
    assert safety.check(text, "data_residency").must_go_to_person


@pytest.mark.parametrize("text", BACKUP_QUESTIONS)
def test_a_backup_replication_question_goes_to_a_person(final_rules, text):
    assert safety.check(text, "data_residency").must_go_to_person


def test_the_data_residency_type_alone_sends_a_ticket_to_a_person(final_rules):
    result = safety.check("Where is it kept?", "data_residency")
    assert result.must_go_to_person and "type: data_residency" in result.reasons


@pytest.mark.parametrize("text", Q20)
def test_export_missing_older_records_is_answered(final_rules, text):
    """14 Nov 2026: the Q20 rule is removed; the customer asks how the snapshot works and the article answers it."""
    assert not safety.check(text, "data_export").must_go_to_person


@pytest.mark.parametrize("text", [
    "We changed the password on our shared account over the weekend and now our automated jobs are all failing to authenticate.",
    "we change password on our shared account around 14:00 yesterday and now our automated jobs all fail to authenticate."])
def test_automated_jobs_failing_after_a_password_change_go_to_a_person(final_rules, text):
    result = safety.check(text, "authentication_failure")
    assert result.must_go_to_person and any("(Q11)" in r for r in result.reasons)


@pytest.mark.parametrize("text", STAY_AUTOMATIC + [
    "We are connecting our CI pipeline and are not sure whether to use a personal key or something else."])    # Q32
def test_questions_decided_automatic_are_not_caught(final_rules, text):
    assert not safety.check(text, "data_export").must_go_to_person


def test_without_the_switch_the_narrowed_rules_answer_data_location_questions(monkeypatch):
    monkeypatch.setenv("NARROW_RULES", "on")
    assert not safety.check("We need our data to remain within the EU for a contract we are signing.",
                            "data_residency").must_go_to_person
    assert not safety.check(Q20[0], "data_export").must_go_to_person
