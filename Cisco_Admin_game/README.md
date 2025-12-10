# Cisco Admin Learning Game

This interactive Tkinter-based learning game is designed to teach Cisco CLI commands, configuration patterns, troubleshooting, and network design principles.

Files:
- `app.py` - Main Tkinter application (Study / Quiz / History tabs).
- `questions.json` - Question bank (easy/medium/hard).
- `study_content.md` - Study content displayed in the Study tab.
- `scores.json` - (created at runtime) saved quiz scores.

How to run:

1. Ensure you have Python 3.8+ installed.
2. From the folder `Cisco_Admin_game` run:

```pwsh
python .\app.py
```

Notes & next steps:
- You can add or edit `questions.json` to extend the question bank. Keep the top-level key `questions` with objects containing `difficulty`, `question`, `choices`, `answer`, and optional `explanation`.
- If you'd like, I can merge questions from your existing `Routing_learning_game` and `Routing_learning_app` into this game at runtime or persist a merged file.
- I can also expand the question bank further, add scenario simulations, or add automated syntax checking before saving new questions.
 - The app now includes a `Labs` tab with guided, step-by-step CLI labs. Labs are defined in `labs.json` and allow you to type commands into a prompt and get simulated feedback.
 - Questions may optionally use a `type` of `cli` and provide an `accepted_answers` array for free-text command matching.

Enjoy learning and tell me if you want more topics added (MPLS, SD-WAN, programmability, platform-specific commands, etc.).
