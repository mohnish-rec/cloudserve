"""11 Nov: type-aware search, for tickets whose wording does not match the documentation (non-fluent English)."""
from src.retrieve import Retriever, search_typed, strip_filler
from tests.test_retrieve import CHUNKS, WordCounter

ONB = {"doc_id": "DOC-ONB-001", "title": "First deployment", "category": "onboarding",
       "text": "A new user does not know where to begin: create a project, then a release. Release, then login."}
LOGIN2 = {"doc_id": "DOC-AUTH-003", "title": "Login 2", "category": "authentication", "text": "login reset password"}
LOGIN3 = {"doc_id": "DOC-AUTH-004", "title": "Login 3", "category": "authentication", "text": "login password"}
CH = CHUNKS + [ONB, LOGIN2, LOGIN3]


def r(**kw):
    return Retriever(CH, WordCounter(), min_similarity=0.3, **kw)


def test_filler_phrases_are_removed_before_searching():
    assert strip_filler("can you please point me at right starting place? waiting for your reply. thanks") == \
        "can you point me at right starting place? ."


def test_the_articles_of_the_tickets_type_are_always_among_those_read():
    q = "login console login password"                              # words pull search to the login articles
    plain = [p.doc_id for p in r().search(q)][:3]
    assert "DOC-ONB-001" not in plain
    typed = [p.doc_id for p in search_typed(r(), q, "onboarding")]
    assert typed[2] == "DOC-ONB-001" and typed[:2] == plain[:2]     # the two best stay first; the type's article third


def test_nothing_changes_when_an_article_of_that_kind_is_already_found():
    q = "How do I revert to an earlier revision of my release?"
    assert [p.doc_id for p in search_typed(r(), q, "rollback_request")] == [p.doc_id for p in r().search(q)]


def test_types_that_always_go_to_a_person_get_nothing_added():
    q = "login console login password"
    assert [p.doc_id for p in search_typed(r(), q, "security_incident")] == [p.doc_id for p in r().search(q)]


def test_an_unrelated_article_of_that_kind_is_not_added():
    assert search_typed(r(), "zzz qqq", "onboarding") == []
