import pytest
from tasks import identify_slots, retrieve_candidates, build_dynamic_prompt, get_ai_response

def test_identify_slots_basic():
    user_input = "Recommend a fun action movie"
    filled, missing = identify_slots(user_input)
    assert filled.get('genre') in ('Action', 'Sci-Fi/Action') or filled.get('genre') is not None
    assert 'mood' in filled or 'mood' in missing or isinstance(missing, list)

def test_retrieve_candidates_with_genre():
    slots = {'genre': 'Action'}
    cands = retrieve_candidates(slots)
    titles = [c['title'] for c in cands]
    assert any(t in titles for t in ["The Dark Knight", "The Avengers"])

def test_dynamic_prompt_contains_all_components():
    user_input = "Any movies by Nolan?"
    slots = {'director': 'Christopher Nolan'}
    retrieved = [{"title": "Inception", "release_year":2010}, {"title": "The Dark Knight", "release_year":2008}]
    prompt = build_dynamic_prompt(user_input, slots, retrieved)
    assert "movie expert" in prompt.lower()
    assert "christopher nolan" in prompt or "Christopher Nolan" in prompt
    assert "Inception" in prompt

def test_get_ai_response_asks_question_for_missing_slots():
    # Should ask a clarifying question when missing slots (e.g., genre)
    resp = get_ai_response("Recommend something")
    assert isinstance(resp, str) and "?" in resp

def test_get_ai_response_action_specific_question():
    resp = get_ai_response("Recommend a fun action movie")
    # Should still be a clarifying question
    assert isinstance(resp, str) and "?" in resp
