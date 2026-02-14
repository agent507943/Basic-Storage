import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import random
import os
from datetime import datetime
import platform
import math

USE_WINSOUND = platform.system() == 'Windows'
if USE_WINSOUND:
    try:
        import winsound
    except Exception:
        USE_WINSOUND = False
else:
    try:
        import pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
    except Exception:
        pygame = None

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
STUDY_FILE = os.path.join(BASE_DIR, "study_content.md")
SETTINGS_FILE = os.path.join(BASE_DIR, "learn_settings.json")

# Optional integration with the original Routing Learning App content
LEGACY_APP_DIR = os.path.join(os.path.dirname(BASE_DIR), "Routing_learning_app")
LEGACY_QUESTIONS_FILE = os.path.join(LEGACY_APP_DIR, "questions.json")
LEGACY_STUDY_FILE = os.path.join(LEGACY_APP_DIR, "study_content.md")

default_settings = {"sound_enabled": True, "theme": "light"}
if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as sf:
            user_settings = json.load(sf)
            default_settings.update(user_settings)
    except Exception:
        pass
settings = default_settings

confetti = []


def spawn_confetti(x, y, count=18):
    for _ in range(count):
        confetti.append({
            'x': x + random.randint(-6, 6),
            'y': y + random.randint(-6, 6),
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-5, -1),
            'age': 0.0,
            'life': random.uniform(0.6, 1.6),
            'color': random.choice(['orange', 'red', 'gold', 'darkgreen', 'purple', 'magenta'])
        })


def update_and_draw_confetti(canvas):
    to_remove = []
    for p in confetti[:]:
        p['age'] += 1.0 / 60.0
        if p['age'] >= p['life']:
            try:
                confetti.remove(p)
            except ValueError:
                pass
            continue
        p['vy'] += 0.2
        p['x'] += p['vx']
        p['y'] += p['vy']
        try:
            canvas.create_rectangle(p['x'], p['y'], p['x'] + 6, p['y'] + 4, fill=p['color'], outline='')
        except Exception:
            pass

def load_all_questions():
    """Load routing questions from this game and, if present, from the original Routing_learning_app.

    Questions are merged and de-duplicated by (difficulty, question text).
    """
    questions = []
    seen = set()
    for path in (QUESTIONS_FILE, LEGACY_QUESTIONS_FILE):
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for q in data:
                            if not isinstance(q, dict):
                                continue
                            key = (q.get("difficulty"), q.get("question"))
                            if key in seen:
                                continue
                            seen.add(key)
                            questions.append(q)
        except Exception:
            # If one source fails, continue with what we have
            continue
    return questions


QUESTIONS = load_all_questions()

DIFFICULTIES = ["easy", "medium", "hard"]
QUESTIONS_BY_DIFF = {d: [q for q in QUESTIONS if q.get("difficulty") == d] for d in DIFFICULTIES}

SCORES_FILE = os.path.join(BASE_DIR, "scores.json")
REVIEW_FILE = os.path.join(BASE_DIR, "review_list.json")


def load_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r", encoding="utf-8") as sf:
                return json.load(sf)
    except Exception:
        pass
    return []


def save_score_record(record):
    scores = load_scores()
    scores.insert(0, record)
    scores = scores[:20]
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as sf:
            json.dump(scores, sf, indent=2)
    except Exception:
        pass


def load_review_list():
    try:
        if os.path.exists(REVIEW_FILE):
            with open(REVIEW_FILE, 'r', encoding='utf-8') as rf:
                return json.load(rf)
    except Exception:
        pass
    return []


def save_review_list(lst):
    try:
        with open(REVIEW_FILE, 'w', encoding='utf-8') as rf:
            json.dump(lst, rf, indent=2)
    except Exception:
        pass


def add_question_to_review(q):
    # store minimal identifying info so questions can be matched later
    try:
        lst = load_review_list()
        key = {'difficulty': q.get('difficulty'), 'question': q.get('question')}
        if key not in lst:
            lst.append(key)
            save_review_list(lst)
    except Exception:
        pass


def clear_review_list():
    try:
        if os.path.exists(REVIEW_FILE):
            os.remove(REVIEW_FILE)
    except Exception:
        pass


def play_sound(kind="correct"):
    if not settings.get("sound_enabled", True):
        return
    try:
        if USE_WINSOUND:
            if kind == "correct":
                winsound.Beep(500, 100)
                winsound.Beep(700, 150)
            elif kind == "wrong":
                winsound.Beep(400, 200)
                winsound.Beep(250, 250)
            elif kind == "finish":
                winsound.Beep(400, 100)
                winsound.Beep(600, 100)
                winsound.Beep(800, 200)
        else:
            if 'pygame' in globals() and pygame and pygame.mixer.get_init():
                if kind == "correct":
                    freqs = [500, 700]
                    durations = [100, 150]
                elif kind == "wrong":
                    freqs = [400, 250]
                    durations = [200, 250]
                else:
                    freqs = [400, 600, 800]
                    durations = [100, 100, 200]

                for freq, duration in zip(freqs, durations):
                    sample_rate = 22050
                    n = int(sample_rate * (duration / 1000.0))
                    arr = bytearray()
                    for i in range(n):
                        t = i / sample_rate
                        v = int(127 + 127 * 0.5 * math.sin(2 * math.pi * freq * t))
                        arr.append(v)
                    try:
                        snd = pygame.mixer.Sound(buffer=bytes(arr))
                        snd.play()
                    except Exception:
                        pass
    except Exception:
        pass


class RoutingLearnApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Learn Routing - Advanced IP Routing")
        self.geometry("800x600")
        self.resizable(False, False)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.study_frame = ttk.Frame(self.nb)
        self.nb.add(self.study_frame, text="Study")
        self._build_study_tab()

        self.quiz_frame = ttk.Frame(self.nb)
        self.nb.add(self.quiz_frame, text="Quiz Game")
        self._build_quiz_tab()

        self.history_frame = ttk.Frame(self.nb)
        self.nb.add(self.history_frame, text="History")
        self._build_history_tab()

    def _build_study_tab(self):
        lbl = ttk.Label(self.study_frame, text="Study: Advanced IP Routing", font=(None, 16))
        lbl.pack(pady=8)

        self.study_text = scrolledtext.ScrolledText(self.study_frame, wrap=tk.WORD)
        self.study_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        # Load this game's study guide and optionally append the broader
        # Routing_learning_app guide if it exists.
        main_content = ""
        legacy_content = ""
        try:
            if os.path.exists(STUDY_FILE):
                with open(STUDY_FILE, "r", encoding="utf-8") as sf:
                    main_content = sf.read()
        except Exception:
            main_content = ""

        try:
            if os.path.exists(LEGACY_STUDY_FILE):
                with open(LEGACY_STUDY_FILE, "r", encoding="utf-8") as sf:
                    legacy_content = sf.read()
        except Exception:
            legacy_content = ""

        if main_content and legacy_content:
            content = main_content + "\n\n---\n\n" + legacy_content
        elif main_content:
            content = main_content
        elif legacy_content:
            content = legacy_content
        else:
            content = "Study content not found."
        self.study_text.insert(tk.END, content)
        self.study_text.configure(state=tk.DISABLED)

    def _build_quiz_tab(self):
        top_frame = ttk.Frame(self.quiz_frame)
        top_frame.pack(fill=tk.X, pady=6)

        ttk.Label(top_frame, text="Select difficulty:").pack(side=tk.LEFT, padx=8)
        self.diff_var = tk.StringVar(value="easy")
        diff_menu = ttk.OptionMenu(top_frame, self.diff_var, "easy", *DIFFICULTIES)
        diff_menu.pack(side=tk.LEFT)

        self.start_btn = ttk.Button(top_frame, text="Start Quiz", command=self.start_quiz)
        self.start_btn.pack(side=tk.LEFT, padx=8)

        self.review_btn = ttk.Button(top_frame, text="Start Review", command=self.start_review)
        self.review_btn.pack(side=tk.LEFT, padx=4)

        self.clear_review_btn = ttk.Button(top_frame, text="Clear Review", command=self._clear_review_prompt)
        self.clear_review_btn.pack(side=tk.LEFT, padx=4)
        self.sound_var = tk.BooleanVar(value=settings.get("sound_enabled", True))
        self.sound_btn = ttk.Checkbutton(top_frame, text="Sound", variable=self.sound_var, command=self._toggle_sound)
        self.sound_btn.pack(side=tk.LEFT, padx=6)

        self.score_var = tk.IntVar(value=0)
        ttk.Label(top_frame, textvariable=self.score_var).pack(side=tk.RIGHT, padx=10)
        ttk.Label(top_frame, text="Score:").pack(side=tk.RIGHT)

        self.progressbar = ttk.Progressbar(top_frame, length=200, maximum=15)
        self.progressbar.pack(side=tk.RIGHT, padx=6)
        self.qcount_var = tk.StringVar(value="0/0")
        ttk.Label(top_frame, textvariable=self.qcount_var).pack(side=tk.RIGHT)

        self.q_frame = ttk.Frame(self.quiz_frame)
        self.q_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.anim_canvas = tk.Canvas(self.q_frame, width=760, height=140, bg=self.cget('bg'), highlightthickness=0)
        self.anim_canvas.pack(pady=(6, 4))

        self.q_label = ttk.Label(self.q_frame, text="Press Start to begin", wraplength=760, font=(None, 14))
        self.q_label.pack(pady=4)

        self.choices_vars = []
        self.choice_buttons = []
        for i in range(4):
            var = tk.StringVar(value="")
            btn = ttk.Button(self.q_frame, textvariable=var, command=lambda i=i: self.submit_answer(i))
            btn.pack(fill=tk.X, pady=4)
            self.choices_vars.append(var)
            self.choice_buttons.append(btn)

        self.feedback_var = tk.StringVar(value="")
        self.feedback_label = ttk.Label(self.q_frame, textvariable=self.feedback_var, font=(None, 12))
        self.feedback_label.pack(pady=6)

        self.expl_text = scrolledtext.ScrolledText(self.q_frame, wrap=tk.WORD, height=4)
        self.expl_text.pack(fill=tk.X, pady=(0, 6))
        self.expl_text.configure(state=tk.DISABLED)

        self.next_btn = ttk.Button(self.q_frame, text="Next", command=self.next_question, state="disabled")
        self.next_btn.pack()

        bottom = ttk.Frame(self.quiz_frame)
        bottom.pack(fill=tk.X, pady=6)
        self.progress_var = tk.StringVar(value="0/0")
        ttk.Label(bottom, textvariable=self.progress_var).pack(side=tk.LEFT, padx=8)
        ttk.Button(bottom, text="Give Up", command=self.end_quiz).pack(side=tk.RIGHT, padx=8)

        self.current_questions = []
        self.current_index = 0
        self.score = 0

    def _build_history_tab(self):
        lbl = ttk.Label(self.history_frame, text="Score History (last 20)", font=(None, 14))
        lbl.pack(pady=8)
        self.history_list = tk.Listbox(self.history_frame, height=15)
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side=tk.RIGHT, padx=6)
        self.update_history_view()

    def update_history_view(self):
        self.history_list.delete(0, tk.END)
        scores = load_scores()
        for rec in scores:
            t = rec.get("time", "")
            s = rec.get("score", 0)
            d = rec.get("difficulty", "")
            pretty = f"{t} | {d} | {s}"
            self.history_list.insert(tk.END, pretty)

    def clear_history(self):
        try:
            if os.path.exists(SCORES_FILE):
                os.remove(SCORES_FILE)
        except Exception:
            pass
        self.update_history_view()

    def _toggle_sound(self):
        settings['sound_enabled'] = bool(self.sound_var.get())
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as sf:
                json.dump(settings, sf)
        except Exception:
            pass

    def _animate_confetti(self):
        try:
            self.anim_canvas.delete('all')
            update_and_draw_confetti(self.anim_canvas)
            if len(confetti) > 0:
                self.after(50, self._animate_confetti)
        except Exception:
            pass

    def start_quiz(self):
        diff = self.diff_var.get()
        pool = QUESTIONS_BY_DIFF.get(diff, [])
        if len(pool) < 15:
            messagebox.showwarning("Not enough questions", f"Only {len(pool)} questions available for {diff}")
            return
        self.current_questions = random.sample(pool, 15)
        self.current_index = 0
        self.score = 0
        self.score_var.set(self.score)
        self._show_question()
        self.progressbar['value'] = 1
        self.qcount_var.set("1/15")

    def _show_question(self):
        q = self.current_questions[self.current_index]
        self.q_label.config(text=f"Q{self.current_index + 1}: {q['question']}")
        choices = q['choices'][:]
        random.shuffle(choices)
        for i, c in enumerate(choices):
            self.choices_vars[i].set(c)
            self.choice_buttons[i].state(["!disabled"])
        self.feedback_var.set("")
        self.next_btn.state(["disabled"])
        self.progress_var.set(f"{self.current_index + 1}/{len(self.current_questions)}")
        try:
            self.qcount_var.set(f"{self.current_index + 1}/{len(self.current_questions)}")
        except Exception:
            pass
        try:
            self.anim_canvas.delete('all')
        except Exception:
            pass
        try:
            self.expl_text.configure(state=tk.NORMAL)
            self.expl_text.delete('1.0', tk.END)
            self.expl_text.configure(state=tk.DISABLED)
        except Exception:
            pass

    def submit_answer(self, choice_index):
        q = self.current_questions[self.current_index]
        selected = self.choices_vars[choice_index].get()
        correct = q['answer']
        for btn in self.choice_buttons:
            btn.state(["disabled"])

        if selected == correct:
            self.score += 10
            self.feedback_var.set("Correct! +10 points")
            try:
                spawn_confetti(360, 20, count=24)
                play_sound('correct')
                self._animate_confetti()
            except Exception:
                pass
        else:
            self.score -= 5
            self.feedback_var.set(f"Wrong. -5 points. Correct: {correct}")
            try:
                spawn_confetti(360, 20, count=12)
                play_sound('wrong')
                self._animate_confetti()
            except Exception:
                pass
            try:
                add_question_to_review(q)
            except Exception:
                pass
        try:
            explanation = q.get('explanation', '')
            if explanation:
                self.expl_text.configure(state=tk.NORMAL)
                self.expl_text.delete('1.0', tk.END)
                self.expl_text.insert(tk.END, explanation)
                self.expl_text.configure(state=tk.DISABLED)
        except Exception:
            pass
        self.score_var.set(self.score)
        self.next_btn.state(["!disabled"])

    def end_quiz(self):
        self.current_questions = []
        self.current_index = 0
        self.score = 0
        self.score_var.set(self.score)
        self.q_label.config(text="Press Start to begin")
        for var in self.choices_vars:
            var.set("")
        for btn in self.choice_buttons:
            btn.state(["disabled"])
        self.progressbar['value'] = 0
        self.progressbar['maximum'] = len(self.current_questions)
        self.progressbar['value'] = 1
        self.qcount_var.set(f"1/{len(self.current_questions)}")

    def start_review(self):
        # load review list and map to actual question objects
        entries = load_review_list()
        if not entries:
            messagebox.showinfo("Review list empty", "No questions in the review list. Answer some questions incorrectly to add them.")
            return
        objs = []
        for ent in entries:
            # find matching question
            matches = [q for q in QUESTIONS if q.get('difficulty') == ent.get('difficulty') and q.get('question') == ent.get('question')]
            if matches:
                objs.append(matches[0])
        if not objs:
            messagebox.showinfo("No matches", "No matching questions found for the saved review list.")
            return
        self.current_questions = objs
        self.current_index = 0
        self.score = 0
        self.score_var.set(self.score)
        self.progressbar['maximum'] = len(self.current_questions)
        self._show_question()
        self.progressbar['value'] = 1
        self.qcount_var.set(f"1/{len(self.current_questions)}")
    def next_question(self):
    def _clear_review_prompt(self):
        if messagebox.askyesno("Clear Review List", "Clear all saved review questions?"):
            clear_review_list()
            messagebox.showinfo("Cleared", "Review list cleared.")
        self.current_index += 1
        if self.current_index >= len(self.current_questions):
            messagebox.showinfo("Quiz finished", f"Final score: {self.score}")
            record = {"score": self.score, "difficulty": self.diff_var.get(), "time": datetime.now().isoformat()}
            save_score_record(record)
            self.update_history_view()
            play_sound('finish')
            self.end_quiz()
            return
        self._show_question()
        self.progressbar['value'] = self.current_index + 1
        self.qcount_var.set(f"{self.current_index + 1}/15")


if __name__ == '__main__':
    app = RoutingLearnApp()
    app.mainloop()
