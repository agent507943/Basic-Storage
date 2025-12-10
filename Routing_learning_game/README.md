# Routing Learning Game

## Overview

An interactive educational application designed to help network professionals and students master advanced IP routing concepts through engaging quizzes and a focused study guide.

## Features

- **Interactive Quiz Interface**: Clean, user-friendly GUI built with tkinter
- **Three Difficulty Levels**: Progressive learning from fundamentals to advanced design and troubleshooting
  - **Easy**: Core definitions, basic CIDR, IGP/BGP roles, timers
  - **Medium**: LPM scenarios, OSPF/BGP behavior, VRFs, MPLS, multicast
  - **Hard**: Complex multi-domain designs, redistribution pitfalls, traffic engineering, and stability issues
- **Custom Sound Effects**: Feedback tones for correct, incorrect, and completed quizzes
- **Progress Tracking**: Visual progress bar, score counter, and history of last 20 quiz attempts
- **Detailed Explanations**: Each question includes a concise explanation to reinforce learning
- **Study Guide Integration**: `study_content.md` provides a structured routing reference

## Routing Topics Covered

- CIDR and route summarization
- Longest Prefix Match (LPM)
- Interior Gateway Protocols (OSPF, IS-IS, EIGRP)
- BGP path selection and attributes
- Route redistribution and filtering
- Convergence tuning (timers, BFD, micro-loops)
- Policy-Based Routing (PBR)
- VRFs and route leaking
- MPLS and Segment Routing basics
- Multicast (PIM, RPF, RP concepts)
- IPv6 routing fundamentals and address types

## Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)
- winsound (Windows) or pygame (for cross-platform audio)

### Setup
1. Place all files in the same directory:
   - `app.py` - Main application
   - `questions.json` - Routing quiz database
   - `study_content.md` - Routing study guide
   - `README.md` - This documentation
2. (Optional) Copy `learn_settings.json` and `scores.json` from the DHCP learning game if you want to reuse settings or history, or let the app create them automatically.

### Running the Application
```bash
python app.py
```

## Usage

1. Start the application with `python app.py`.
2. Use the **Study** tab to review routing concepts.
3. Switch to the **Quiz Game** tab, choose a difficulty, and click **Start Quiz**.
4. Answer multiple-choice questions, review explanations, and track your score.
5. Use the **History** tab to review the last 20 quiz results.

## Customization

- Edit `questions.json` to add or modify routing questions.
- Extend `study_content.md` with your own notes or lab topologies.
- Adjust sound behavior by toggling the Sound checkbox in the UI (stored in `learn_settings.json`).

This game is modeled after the DHCP learning game structure, adapted specifically for advanced routing topics.
