# Routing Learning

A single, consolidated interactive routing quiz + study application. This merges what used to be two separate projects (`Routing_learning_app` and `Routing_learning_game`) into one app with the full combined question bank and every feature from both.

## Features

- **Tabbed interface**: Study / Quiz Game / History
- **112 merged, deduplicated questions** (39 easy / 40 medium / 33 hard) combining both original question banks
- **Configurable quiz length**: choose 10, 15, 20, or 25 questions per session (capped to what's available per difficulty)
- **Three difficulty levels**: easy, medium, hard
- **Score tracking**: +10 for correct, -5 for incorrect, live score display
- **Performance summary on completion**: percentage score plus a tiered performance message (Outstanding / Excellent / Good / Not bad / Keep learning)
- **Celebratory confetti animation**: on every correct answer, and a bigger celebration when you score 90%+ on a quiz
- **Route Lab visualizer**: interactive longest-prefix-match demo with a live topology canvas, route table, and best-path explanation
- **OSPF Lab visualizer**: area-boundary, DR/BDR, and LSA flow diagram for Cisco routing exam concepts
- **Missed-question review list**: incorrect answers are automatically saved; use "Start Review" to retake just the questions you missed, "Clear Review" to reset it
- **Score history**: last 20 quiz attempts (score, percentage, difficulty, timestamp) saved to `scores.json` and viewable in the History tab
- **Sound effects**: distinct tones for correct/wrong/finish, with a Sound toggle persisted to `learn_settings.json`; uses `winsound` on Windows and falls back to `pygame`-generated tones elsewhere
- **Detailed explanations**: shown after each answer to reinforce learning
- **Help button / hint dock**: click "💡 Help" on any question to reveal a clue that nudges you toward the answer without giving it away outright
- **Consolidated study guide** (`study_content.md`): combines the original beginner-to-advanced curriculum (fundamentals, protocols, security, troubleshooting) with the advanced IP routing reference (CIDR/LPM, BGP deep dive, redistribution, convergence, VRFs, MPLS, multicast, IPv6)

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)
- winsound (Windows) or pygame (for cross-platform audio)

### Setup
All files live in this one folder:
- `app.py` - Main application
- `questions.json` - Merged routing quiz database (112 questions)
- `study_content.md` - Merged routing study guide
- `README.md` - This documentation

`learn_settings.json`, `scores.json`, and `review_list.json` are created automatically as you use the app.

### Running the Application
```bash
python app.py
```

## Usage

1. Start the application with `python app.py`.
2. Use the **Study** tab to review routing concepts.
3. Use the **Route Lab** tab to visualize longest-prefix match, administrative distance, and path selection on a live topology.
4. Use the **OSPF Lab** tab to see area boundaries, DR/BDR election, and LSA flow.
5. Switch to the **Quiz Game** tab, choose a difficulty and number of questions, then click **Start Quiz**.
6. Stuck on a question? Click **💡 Help** to reveal a hint before answering.
7. Answer multiple-choice questions, review explanations, and track your score.
8. Missed questions are added to the review list — click **Start Review** any time to retake just those.
9. Use the **History** tab to review the last 20 quiz results.

## Customization

- Edit `questions.json` to add or modify routing questions.
- Extend `study_content.md` with your own notes or lab topologies.
- Toggle sound behavior via the Sound checkbox in the Quiz Game tab (stored in `learn_settings.json`).

## History

This app replaces the previous `Routing_learning_app` and `Routing_learning_game` folders, which covered the same topic with overlapping but incomplete feature sets (and the latter had a code bug preventing it from running). All content and functionality from both has been merged here.

## Product Intent

The current application is implemented in Python with tkinter for rapid local learning workflows.

Planned direction:
- Keep this Python version stable for current use.
- Migrate the user interface to a TypeScript-based frontend for stronger UX/UI (interactive diagrams, richer animations, improved layout flexibility).
- Preserve existing learning assets and logic during migration (`questions.json`, `study_content.md`, scoring/history/review behavior, and visual labs).

Migration goal:
- Deliver a modern exam-prep experience for advanced Cisco routing topics while maintaining feature parity with the Python app during transition.
