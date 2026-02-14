import json
import os

BASE_DIR = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
QFILE = os.path.join(ROOT, 'questions.json')


def test_questions_loadable():
    with open(QFILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)


def test_question_schema():
    with open(QFILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for q in data:
        assert 'question' in q and isinstance(q['question'], str)
        assert 'difficulty' in q and q['difficulty'] in ('easy', 'medium', 'hard')
        qtype = q.get('type', 'mcq')
        if qtype == 'multiple':
            assert isinstance(q.get('choices', []), list)
            assert isinstance(q.get('answer', None), list)
            assert len(q.get('answer', [])) >= 1
        elif qtype == 'text':
            assert 'answer' in q and isinstance(q['answer'], str)
        else:
            assert isinstance(q.get('choices', []), list)
            assert 'answer' in q and isinstance(q['answer'], str)