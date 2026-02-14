import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
import random
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
STUDY_FILE = os.path.join(BASE_DIR, "study_content.md")
SCORES_FILE = os.path.join(BASE_DIR, "scores.json")
REVIEW_FILE = os.path.join(BASE_DIR, "review_list.json")


def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def load_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r', encoding='utf-8') as sf:
                return json.load(sf)
    except Exception:
        pass
    return []


def save_score_record(record):
    scores = load_scores()
    scores.insert(0, record)
    scores = scores[:50]
    try:
        with open(SCORES_FILE, 'w', encoding='utf-8') as sf:
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


class WebSecLearnApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Web Security Learning")
        self.geometry("820x620")
        self.resizable(False, False)

        self.questions = load_questions()

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.study_frame = ttk.Frame(self.nb)
        self.nb.add(self.study_frame, text="Study")
        self._build_study_tab()

        self.quiz_frame = ttk.Frame(self.nb)
        self.nb.add(self.quiz_frame, text="Quiz")
        self._build_quiz_tab()

        self.history_frame = ttk.Frame(self.nb)
        self.nb.add(self.history_frame, text="History")
        self._build_history_tab()

    def _build_study_tab(self):
        lbl = ttk.Label(self.study_frame, text="Study: Web Security Topics", font=(None, 16))
        lbl.pack(pady=8)
        self.study_text = scrolledtext.ScrolledText(self.study_frame, wrap=tk.WORD)
        self.study_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        content = "Study content not found."
        try:
            if os.path.exists(STUDY_FILE):
                with open(STUDY_FILE, 'r', encoding='utf-8') as sf:
                    content = sf.read()
        except Exception:
            pass
        self.study_text.insert(tk.END, content)
        self.study_text.configure(state=tk.DISABLED)

    def _build_quiz_tab(self):
        top = ttk.Frame(self.quiz_frame)
        top.pack(fill=tk.X, pady=6)
        ttk.Label(top, text="Difficulty:").pack(side=tk.LEFT, padx=6)
        self.diff_var = tk.StringVar(value="all")
        diff_menu = ttk.OptionMenu(top, self.diff_var, "all", "all", "easy", "medium", "hard")
        diff_menu.pack(side=tk.LEFT)

        ttk.Label(top, text="Questions:").pack(side=tk.LEFT, padx=(10,2))
        self.num_var = tk.IntVar(value=20)
        self.num_spin = tk.Spinbox(top, from_=5, to=200, width=5, textvariable=self.num_var)
        self.num_spin.pack(side=tk.LEFT)

        # Theme and accessibility controls
        ttk.Label(top, text="Theme:").pack(side=tk.LEFT, padx=(10,2))
        self.theme_var = tk.StringVar(value='light')
        theme_menu = ttk.OptionMenu(top, self.theme_var, 'light', 'light', 'dark', 'high-contrast', command=self._apply_theme)
        theme_menu.pack(side=tk.LEFT)
        ttk.Label(top, text="Font:").pack(side=tk.LEFT, padx=(8,2))
        self.font_var = tk.IntVar(value=10)
        self.font_spin = tk.Spinbox(top, from_=10, to=20, width=3, textvariable=self.font_var, command=self._apply_font)
        self.font_spin.pack(side=tk.LEFT)

        self.start_btn = ttk.Button(top, text="Start Quiz", command=self.start_quiz)
        self.start_btn.pack(side=tk.LEFT, padx=6)

        self.review_btn = ttk.Button(top, text="Start Review", command=self.start_review)
        self.review_btn.pack(side=tk.LEFT, padx=4)

        self.clear_review_btn = ttk.Button(top, text="Clear Review", command=self._clear_review_prompt)
        self.clear_review_btn.pack(side=tk.LEFT, padx=4)

        ttk.Button(top, text="Import Questions", command=self.import_questions).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Export Questions", command=self.export_questions).pack(side=tk.LEFT, padx=4)

        self.score_var = tk.IntVar(value=0)
        ttk.Label(top, textvariable=self.score_var).pack(side=tk.RIGHT, padx=10)
        ttk.Label(top, text="Score:").pack(side=tk.RIGHT)

        self.qcount_var = tk.StringVar(value="0/0")
        ttk.Label(top, textvariable=self.qcount_var).pack(side=tk.RIGHT, padx=8)

        self.progress = ttk.Progressbar(top, length=180, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=6)

        self.review_count_var = tk.StringVar(value=str(len(load_review_list())))
        ttk.Label(top, text="Review:").pack(side=tk.RIGHT)
        ttk.Label(top, textvariable=self.review_count_var).pack(side=tk.RIGHT, padx=4)

        self.q_frame = ttk.Frame(self.quiz_frame)
        self.q_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.q_label = ttk.Label(self.q_frame, text="Press Start to begin", wraplength=760, font=(None, 14))
        self.q_label.pack(pady=8)

        # container for choice widgets; these will be generated per-question-type
        self.choice_frame = ttk.Frame(self.q_frame)
        self.choice_frame.pack(fill=tk.X)
        self.choices_vars = []
        self.choice_buttons = []
        self.multi_vars = []
        self.text_entry = None

        self.feedback_var = tk.StringVar(value="")
        self.feedback_label = ttk.Label(self.q_frame, textvariable=self.feedback_var)
        self.feedback_label.pack(pady=6)

        self.expl_text = scrolledtext.ScrolledText(self.q_frame, wrap=tk.WORD, height=6)
        self.expl_text.pack(fill=tk.X, pady=(0, 6))
        self.expl_text.configure(state=tk.DISABLED)

        self.next_btn = ttk.Button(self.q_frame, text="Next", command=self.next_question, state="disabled")
        self.next_btn.pack()

        bottom = ttk.Frame(self.quiz_frame)
        bottom.pack(fill=tk.X, pady=6)
        ttk.Button(bottom, text="Give Up", command=self.end_quiz).pack(side=tk.RIGHT, padx=8)

        self.current_questions = []
        self.current_index = 0
        self.score = 0

        # Keyboard shortcuts 1-4 for choices
        for i in range(4):
            self.bind(str(i+1), lambda e, i=i: self._on_key_choice(i))

    def _on_key_choice(self, i):
        try:
            state = self.choice_buttons[i].state()
            if 'disabled' in state:
                return
        except Exception:
            pass
        self.submit_answer(i)

    def _build_history_tab(self):
        lbl = ttk.Label(self.history_frame, text="Score History (last 50)", font=(None, 14))
        lbl.pack(pady=8)
        self.history_list = tk.Listbox(self.history_frame, height=18)
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side=tk.RIGHT, padx=6)
        self.update_history_view()

    def _apply_font(self, *_):
        try:
            size = int(self.font_var.get())
        except Exception:
            size = 10
        default_font = (None, size)
        for widget in (self.q_label, self.feedback_label):
            try:
                widget.config(font=default_font)
            except Exception:
                pass

    def _apply_theme(self, *_):
        t = self.theme_var.get()
        style = ttk.Style()
        if t == 'dark':
            self.configure(bg='#2e2e2e')
            style.configure('.', background='#2e2e2e', foreground='white')
        elif t == 'high-contrast':
            self.configure(bg='black')
            style.configure('.', background='black', foreground='yellow', font=(None, 12, 'bold'))
        else:
            self.configure(bg=None)
            style.configure('.', background=None, foreground=None)

    def import_questions(self):
        path = filedialog.askopenfilename(title='Import question JSON', filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # simple validation: must be list
            if isinstance(data, list):
                with open(QUESTIONS_FILE, 'w', encoding='utf-8') as wf:
                    json.dump(data, wf, indent=2)
                self.questions = data
                messagebox.showinfo('Imported', 'Questions imported successfully')
            else:
                messagebox.showerror('Invalid', 'JSON must be a list of questions')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to import: {e}')

    def export_questions(self):
        path = filedialog.asksaveasfilename(title='Export question JSON', defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as wf:
                json.dump(self.questions, wf, indent=2)
            messagebox.showinfo('Exported', 'Questions exported successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export: {e}')

    def update_history_view(self):
        self.history_list.delete(0, tk.END)
        for rec in load_scores():
            t = rec.get('time', '')
            s = rec.get('score', 0)
            d = rec.get('mode', '')
            pretty = f"{t} | {d} | {s}"
            self.history_list.insert(tk.END, pretty)

    def clear_history(self):
        try:
            if os.path.exists(SCORES_FILE):
                os.remove(SCORES_FILE)
        except Exception:
            pass
        self.update_history_view()

    def start_quiz(self):
        diff = self.diff_var.get()
        pool = [q for q in self.questions if diff == 'all' or q.get('difficulty') == diff]
        if not pool:
            messagebox.showwarning('No questions', 'No questions available for that difficulty')
            return
        # sample up to user-selected number (default 20)
        try:
            requested = int(self.num_var.get())
        except Exception:
            requested = 20
        n = min(max(1, requested), len(pool))
        self.current_questions = random.sample(pool, n)
        self.current_index = 0
        self.score = 0
        self.score_var.set(self.score)
        self._show_question()
        self.qcount_var.set(f"1/{len(self.current_questions)}")
        try:
            self.progress['maximum'] = len(self.current_questions)
            self.progress['value'] = 1
        except Exception:
            pass

    def _show_question(self):
        q = self.current_questions[self.current_index]
        self.q_label.config(text=f"Q{self.current_index+1}: {q.get('question')}")
        # clear previous choice widgets
        for child in self.choice_frame.winfo_children():
            child.destroy()
        self.choices_vars = []
        self.choice_buttons = []
        self.multi_vars = []
        self.text_entry = None

        qtype = q.get('type', 'mcq')
        if qtype == 'multiple':
            # multiple-correct: render checkboxes
            choices = q.get('choices', [])[:]
            for i, c in enumerate(choices):
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(self.choice_frame, text=c, variable=var)
                cb.pack(fill=tk.X, pady=2)
                self.multi_vars.append((var, c))
        elif qtype == 'text':
            # text input answer
            self.text_entry = ttk.Entry(self.choice_frame)
            self.text_entry.pack(fill=tk.X, pady=4)
        else:
            # default multiple choice (single correct)
            choices = q.get('choices', [])[:]
            random.shuffle(choices)
            for i, c in enumerate(choices):
                var = tk.StringVar(value=c)
                btn = ttk.Button(self.choice_frame, text=c, command=lambda i=i: self.submit_answer(i))
                btn.pack(fill=tk.X, pady=4)
                self.choices_vars.append(var)
                self.choice_buttons.append(btn)
        self.feedback_var.set('')
        self.next_btn.state(['disabled'])
        self.qcount_var.set(f"{self.current_index+1}/{len(self.current_questions)}")
        try:
            self.progress['maximum'] = len(self.current_questions)
            self.progress['value'] = self.current_index+1
        except Exception:
            pass
        try:
            self.expl_text.configure(state=tk.NORMAL)
            self.expl_text.delete('1.0', tk.END)
            self.expl_text.configure(state=tk.DISABLED)
        except Exception:
            pass

    def submit_answer(self, idx):
        q = self.current_questions[self.current_index]
        qtype = q.get('type', 'mcq')
        correct = q.get('answer')
        # handle multiple-correct checkboxes
        if qtype == 'multiple':
            selected = [c for var, c in self.multi_vars if var.get()]
            try:
                if set([s.strip().lower() for s in selected]) == set([a.strip().lower() for a in correct]):
                    self.score += 10
                    self.feedback_var.set('Correct! +10')
                else:
                    self.score -= 5
                    self.feedback_var.set(f"Wrong. -5. Correct: {', '.join(correct)}")
                    add_question_to_review(q)
            except Exception:
                self.score -= 5
                self.feedback_var.set(f"Wrong. -5. Correct: {', '.join(correct)}")
                add_question_to_review(q)
        elif qtype == 'text':
            ans = ''
            try:
                ans = self.text_entry.get().strip()
            except Exception:
                ans = ''
            if ans.lower() == str(correct).strip().lower():
                self.score += 10
                self.feedback_var.set('Correct! +10')
            else:
                self.score -= 5
                self.feedback_var.set(f"Wrong. -5. Correct: {correct}")
                add_question_to_review(q)
        else:
            # mcq (single choice buttons)
            try:
                selected = self.choices_vars[idx].get()
            except Exception:
                selected = ''
            for btn in self.choice_buttons:
                btn.state(['disabled'])
            if selected == correct:
                self.score += 10
                self.feedback_var.set('Correct! +10')
            else:
                self.score -= 5
                self.feedback_var.set(f"Wrong. -5. Correct: {correct}")
                add_question_to_review(q)
        try:
            self.review_count_var.set(str(len(load_review_list())))
        except Exception:
            pass
        self.score_var.set(self.score)
        # show explanation if present
        expl = q.get('explanation', '')
        if expl:
            try:
                self.expl_text.configure(state=tk.NORMAL)
                self.expl_text.delete('1.0', tk.END)
                self.expl_text.insert(tk.END, expl)
                self.expl_text.configure(state=tk.DISABLED)
            except Exception:
                messagebox.showinfo('Explanation', expl)
        self.next_btn.state(['!disabled'])

    def next_question(self):
        self.current_index += 1
        if self.current_index >= len(self.current_questions):
            messagebox.showinfo('Finished', f'Final score: {self.score}')
            record = {'score': self.score, 'mode': self.diff_var.get(), 'time': datetime.now().isoformat()}
            save_score_record(record)
            self.update_history_view()
            self.end_quiz()
            return
        self._show_question()
        try:
            self.progress['value'] = self.current_index+1
            self.qcount_var.set(f"{self.current_index+1}/{len(self.current_questions)}")
        except Exception:
            pass

    def end_quiz(self):
        self.current_questions = []
        self.current_index = 0
        self.score = 0
        self.score_var.set(self.score)
        self.q_label.config(text='Press Start to begin')
        for var in self.choices_vars:
            var.set('')
        for btn in self.choice_buttons:
            btn.state(['disabled'])
        self.qcount_var.set('0/0')

    def start_review(self):
        entries = load_review_list()
        if not entries:
            messagebox.showinfo('Review empty', 'No questions in the review list yet.')
            return
        objs = []
        for ent in entries:
            matches = [q for q in self.questions if q.get('difficulty') == ent.get('difficulty') and q.get('question') == ent.get('question')]
            if matches:
                objs.append(matches[0])
        if not objs:
            messagebox.showinfo('No matches', 'Saved review questions could not be resolved.')
            return
        self.current_questions = objs
        self.current_index = 0
        self.score = 0
        self.score_var.set(self.score)
        self._show_question()
        self.qcount_var.set(f"1/{len(self.current_questions)}")
        try:
            self.progress['maximum'] = len(self.current_questions)
            self.progress['value'] = 1
        except Exception:
            pass

    def _clear_review_prompt(self):
        if messagebox.askyesno('Clear Review', 'Clear saved review questions?'):
            clear_review_list()
            messagebox.showinfo('Cleared', 'Review list cleared.')


if __name__ == '__main__':
    app = WebSecLearnApp()
    app.mainloop()
