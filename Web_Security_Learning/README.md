# Web Security Learning (mini app)

Simple Tkinter-based learning app focused on web security topics: TLS, certificates, API security, MFA, and more.

Run:

```bash
python Basic-Storage/Web_Security_Learning/app.py
```

Files:
- `app.py` — main Tkinter application (Study, Quiz, History, Review)
- `questions.json` — question bank
- `study_content.md` — study notes
- `scores.json` and `review_list.json` — created at runtime to persist history and review items

Dependencies: Python 3 with Tkinter (usually included with standard installs).

Developer
---------
- Run tests:

```bash
cd Basic-Storage/Web_Security_Learning
pip install -r requirements-dev.txt
pytest
```

You can import/export question banks from the Quiz tab using the `Import Questions` / `Export Questions` buttons.
