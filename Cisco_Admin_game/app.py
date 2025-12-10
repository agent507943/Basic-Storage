import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import random
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')
STUDY_FILE = os.path.join(BASE_DIR, 'study_content.md')
SCORES_FILE = os.path.join(BASE_DIR, 'scores.json')
LABS_FILE = os.path.join(BASE_DIR, 'labs.json')

class CiscoAdminGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Cisco Admin Learning Game')
        self.geometry('900x600')
        self.questions = self.load_questions()
        self.create_widgets()
        self.current_quiz = []
        self.current_index = 0
        self.score = 0

    def load_questions(self):
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load questions: {e}')
            return []

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        # Study tab
        study_frame = ttk.Frame(notebook)
        notebook.add(study_frame, text='Study')
        # Search bar for study content
        search_frame = ttk.Frame(study_frame)
        search_frame.pack(fill='x', padx=6, pady=(6,2))
        ttk.Label(search_frame, text='Search Study:').pack(side='left')
        self.study_search_var = tk.StringVar()
        self.study_search_entry = ttk.Entry(search_frame, textvariable=self.study_search_var, width=60)
        self.study_search_entry.pack(side='left', padx=(6,4))
        ttk.Button(search_frame, text='Find', command=self.search_study).pack(side='left')
        ttk.Button(search_frame, text='Clear', command=self.clear_search).pack(side='left', padx=4)
        # place study text inside a frame with a vertical scrollbar
        study_text_frame = ttk.Frame(study_frame)
        study_text_frame.pack(fill='both', expand=True, padx=6, pady=(0,6))
        self.study_text = tk.Text(study_text_frame, wrap='word')
        vsb = ttk.Scrollbar(study_text_frame, orient='vertical', command=self.study_text.yview)
        self.study_text.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.study_text.pack(side='left', fill='both', expand=True)
        self.load_study()
        # configure search tag
        self.study_text.tag_configure('search', background='yellow')
        # bind Enter in search entry
        self.study_search_entry.bind('<Return>', lambda e: self.search_study())

        # Quiz tab
        quiz_frame = ttk.Frame(notebook)
        notebook.add(quiz_frame, text='Quiz')
        top_frame = ttk.Frame(quiz_frame)
        top_frame.pack(fill='x')
        ttk.Label(top_frame, text='Difficulty:').pack(side='left', padx=4)
        self.difficulty_var = tk.StringVar(value='medium')
        ttk.Combobox(top_frame, textvariable=self.difficulty_var, values=['easy','medium','hard'], width=8).pack(side='left')
        ttk.Button(top_frame, text='Start Quiz', command=self.start_quiz).pack(side='left', padx=8)
        ttk.Button(top_frame, text='Shuffle Questions', command=self.shuffle_all).pack(side='left', padx=8)
        ttk.Label(top_frame, text='Timer (sec):').pack(side='left', padx=(12,4))
        self.timer_var = tk.IntVar(value=0)
        ttk.Spinbox(top_frame, from_=0, to=300, width=6, textvariable=self.timer_var).pack(side='left')

        status_frame = ttk.Frame(quiz_frame)
        status_frame.pack(fill='x', pady=(6,0))
        self.progress_label = ttk.Label(status_frame, text='Progress: 0/0')
        self.progress_label.pack(side='left', padx=6)
        self.score_label = ttk.Label(status_frame, text='Score: 0')
        self.score_label.pack(side='right', padx=6)

        self.question_var = tk.StringVar()
        self.q_label = ttk.Label(quiz_frame, textvariable=self.question_var, wraplength=800, justify='left', anchor='w')
        self.q_label.pack(pady=12, anchor='w')

        self.choices_frame = ttk.Frame(quiz_frame)
        self.choices_frame.pack(fill='x')
        self.choice_buttons = []

        control_frame = ttk.Frame(quiz_frame)
        control_frame.pack(pady=12, fill='x')
        self.submit_btn = ttk.Button(control_frame, text='Submit Answer', command=self.submit_answer, state='disabled')
        self.submit_btn.pack(side='left', padx=6)
        self.explain_btn = ttk.Button(control_frame, text='Show Explanation', command=self.show_explanation, state='disabled')
        self.explain_btn.pack(side='left', padx=6)
        self.next_btn = ttk.Button(control_frame, text='Next Question', command=self.next_question, state='disabled')
        self.next_btn.pack(side='left', padx=6)
        ttk.Button(control_frame, text='End Quiz', command=self.finish_quiz).pack(side='right', padx=6)

        self.timer_label = ttk.Label(control_frame, text='')
        self.timer_label.pack(side='right', padx=6)

        # History tab
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text='History')
        ttk.Button(history_frame, text='View Scores', command=self.view_scores).pack(pady=8)
        ttk.Button(history_frame, text='Clear Scores', command=self.clear_scores).pack()

        # Labs tab - guided, step-by-step CLI labs
        labs_frame = ttk.Frame(notebook)
        notebook.add(labs_frame, text='Labs')
        left = ttk.Frame(labs_frame)
        left.pack(side='left', fill='y', padx=6, pady=6)
        ttk.Label(left, text='Available Labs').pack()
        self.labs_listbox = tk.Listbox(left, height=8)
        self.labs_listbox.pack(fill='y')
        ttk.Button(left, text='Start Lab', command=self.start_lab).pack(pady=6)

        right = ttk.Frame(labs_frame)
        right.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        self.lab_title = ttk.Label(right, text='Select a lab and click Start Lab', font=('Segoe UI', 12, 'bold'))
        self.lab_title.pack(anchor='w')
        self.lab_text = tk.Text(right, height=12, wrap='word')
        self.lab_text.pack(fill='both', expand=False, pady=(6,8))
        self.lab_step_label = ttk.Label(right, text='Step:')
        self.lab_step_label.pack(anchor='w')
        self.lab_cmd_entry = ttk.Entry(right, width=120)
        self.lab_cmd_entry.pack(fill='x', pady=4)
        ttk.Button(right, text='Submit Command', command=self.submit_lab_command).pack(pady=4)
        self.lab_output = tk.Text(right, height=10, wrap='word')
        self.lab_output.pack(fill='both', expand=True)
        self.labs = self.load_labs()
        for lab in self.labs:
            self.labs_listbox.insert(tk.END, lab.get('title'))

    def load_study(self):
        content = ''
        try:
            with open(STUDY_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            content = '# Study content not found.\nAdd `study_content.md` to the game folder.'
        # keep a copy for searching
        self.study_content = content
        self.study_text.delete('1.0', tk.END)
        self.study_text.insert(tk.END, content)

    def search_study(self):
        query = (self.study_search_var.get() or '').strip()
        self.clear_search()
        if not query:
            messagebox.showinfo('Search', 'Enter a search term or command to find in the study guide.')
            return
        start = '1.0'
        found = 0
        while True:
            idx = self.study_text.search(query, start, stopindex=tk.END, nocase=1)
            if not idx:
                break
            end = f"{idx}+{len(query)}c"
            self.study_text.tag_add('search', idx, end)
            found += 1
            start = end
        if found:
            # show first occurrence
            first = self.study_text.tag_ranges('search')
            if first:
                self.study_text.see(first[0])
            messagebox.showinfo('Search Results', f'Found {found} matches for "{query}"')
        else:
            messagebox.showinfo('Search Results', f'No matches for "{query}"')

    def clear_search(self):
        try:
            self.study_text.tag_remove('search', '1.0', tk.END)
        except Exception:
            pass

    def shuffle_all(self):
        random.shuffle(self.questions)
        messagebox.showinfo('Shuffled', 'All questions shuffled in memory.')

    def load_labs(self):
        if not os.path.exists(LABS_FILE):
            return []
        try:
            with open(LABS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('labs', [])
        except Exception:
            return []

    def start_quiz(self):
        diff = self.difficulty_var.get()
        self.current_quiz = [q for q in self.questions if q.get('difficulty') == diff]
        if not self.current_quiz:
            messagebox.showwarning('No Questions', f'No questions found for difficulty: {diff}')
            return
        random.shuffle(self.current_quiz)
        self.current_index = 0
        self.score = 0
        self.review_items = []
        self.show_current_question()

    def show_current_question(self):
        q = self.current_quiz[self.current_index]
        total = len(self.current_quiz)
        self.progress_label.config(text=f'Progress: {self.current_index+1}/{total}')
        self.score_label.config(text=f'Score: {self.score}')
        self.question_var.set(f"Q{self.current_index+1}: {q['question']}")
        # clear choices
        for cb in self.choice_buttons:
            cb.destroy()
        self.choice_buttons = []
        qtype = q.get('type', 'mcq')
        # remove any CLI entry if previously present
        try:
            if hasattr(self, 'cli_entry') and self.cli_entry:
                self.cli_entry.destroy()
        except Exception:
            pass
        if qtype == 'cli':
            # show a text entry for CLI command input
            self.cli_entry = ttk.Entry(self.choices_frame, width=120)
            self.cli_entry.pack(fill='x', pady=2)
            # pre-enable submit so the user can type and submit
            self.submit_btn.config(state='normal')
            self.next_btn.config(state='disabled')
            self.explain_btn.config(state='disabled')
        else:
            self.answer_var = tk.StringVar()
            choices = q.get('choices', [])
            for c in choices:
                rb = ttk.Radiobutton(self.choices_frame, text=c, variable=self.answer_var, value=c, command=self.enable_submit)
                rb.pack(anchor='w', pady=2, fill='x')
            self.submit_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            self.explain_btn.config(state='disabled')
            self.choice_buttons.append(rb)
        self.submit_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
        self.explain_btn.config(state='disabled')
        # start timer if set
        self.stop_timer()
        secs = int(self.timer_var.get() or 0)
        if secs > 0:
            self.question_time_left = secs
            self.update_timer_label()
            self.timer_job = self.after(1000, self._tick_timer)
        else:
            self.timer_label.config(text='')

    def enable_submit(self):
        self.submit_btn.config(state='normal')

    def _tick_timer(self):
        self.question_time_left -= 1
        self.update_timer_label()
        if self.question_time_left <= 0:
            # timeout: treat as incorrect and move on
            messagebox.showinfo('Time Up', 'Time expired for this question.')
            self.submit_answer(timeout=True)
        else:
            self.timer_job = self.after(1000, self._tick_timer)

    def update_timer_label(self):
        self.timer_label.config(text=f'Time left: {self.question_time_left}s')

    def stop_timer(self):
        try:
            if hasattr(self, 'timer_job') and self.timer_job:
                self.after_cancel(self.timer_job)
        except Exception:
            pass
        self.timer_job = None

    def submit_answer(self, timeout=False):
        # evaluate the selected answer and enable explanation/next
        self.stop_timer()
        q = self.current_quiz[self.current_index]
        qtype = q.get('type', 'mcq')
        if qtype == 'cli':
            selected = self.cli_entry.get().strip() if hasattr(self, 'cli_entry') else ''
        else:
            selected = self.answer_var.get() if hasattr(self, 'answer_var') else ''
        correct = q.get('answer')
        if timeout:
            messagebox.showinfo('Result', f'Timeout. Correct answer: {correct}')
        else:
            if qtype == 'cli':
                # compare against accepted answers list (case-insensitive)
                accepted = q.get('accepted_answers', [])
                ok = any(a.strip().lower() == selected.lower() for a in accepted)
                if ok:
                    self.score += 1
                    messagebox.showinfo('Result', 'Correct CLI command')
                else:
                    messagebox.showinfo('Result', f'Incorrect command. Expected one of: {accepted}')
            else:
                if selected == correct:
                    self.score += 1
                    messagebox.showinfo('Result', 'Correct!')
                else:
                    messagebox.showinfo('Result', f'Incorrect. Correct answer: {correct}')
        # record for review
        self.review_items.append({
            'question': q.get('question'),
            'chosen': selected,
            'correct': correct,
            'explanation': q.get('explanation', '')
        })
        self.score_label.config(text=f'Score: {self.score}')
        self.explain_btn.config(state='normal')
        self.next_btn.config(state='normal')
        self.submit_btn.config(state='disabled')

    # Labs handling
    def start_lab(self):
        sel = self.labs_listbox.curselection()
        if not sel:
            messagebox.showwarning('Select Lab', 'Select a lab from the list first')
            return
        idx = sel[0]
        self.current_lab = self.labs[idx]
        self.lab_step = 0
        self.lab_title.config(text=self.current_lab.get('title', 'Lab'))
        self.show_lab_step()

    def show_lab_step(self):
        steps = self.current_lab.get('steps', [])
        if self.lab_step >= len(steps):
            messagebox.showinfo('Lab Complete', 'You completed the lab!')
            return
        step = steps[self.lab_step]
        self.lab_text.delete('1.0', tk.END)
        self.lab_text.insert(tk.END, step.get('description', ''))
        self.lab_step_label.config(text=f"Step {self.lab_step+1}/{len(steps)}: {step.get('title','')}")
        self.lab_cmd_entry.delete(0, tk.END)
        self.lab_output.delete('1.0', tk.END)

    def submit_lab_command(self):
        if not hasattr(self, 'current_lab'):
            messagebox.showwarning('No Lab', 'Start a lab first')
            return
        steps = self.current_lab.get('steps', [])
        step = steps[self.lab_step]
        entered = self.lab_cmd_entry.get().strip()
        expected = step.get('expected', [])
        ok = any(e.strip().lower() == entered.lower() for e in expected)
        if ok:
            out = step.get('success_output', 'Command accepted.')
            self.lab_output.insert(tk.END, out + '\n')
            self.lab_step += 1
            self.after(300, self.show_lab_step)
        else:
            self.lab_output.insert(tk.END, f"Incorrect command. Expected one of: {expected}\n")

    def next_question(self):
        # move to next question (called after submit and explanation optional)
        self.stop_timer()
        if self.current_index + 1 < len(self.current_quiz):
            self.current_index += 1
            self.show_current_question()
        else:
            self.finish_quiz()

    def show_explanation(self):
        q = self.current_quiz[self.current_index]
        expl = q.get('explanation', 'No explanation provided.')
        messagebox.showinfo('Explanation', expl)

    def finish_quiz(self):
        total = len(self.current_quiz)
        name = simpledialog.askstring('Save Score', 'Enter your name to save the score (or Cancel to skip):')
        result = f'Score: {self.score}/{total}'
        messagebox.showinfo('Quiz Finished', result)
        if name:
            self.save_score(name, self.score, total)
        # show review of answered questions
        if self.review_items:
            self.show_review()

    def show_review(self):
        popup = tk.Toplevel(self)
        popup.title('Review Answers')
        txt = tk.Text(popup, wrap='word')
        txt.pack(fill='both', expand=True)
        for i, it in enumerate(self.review_items, start=1):
            q = it['question']
            chosen = it.get('chosen', '<none>')
            correct = it.get('correct')
            expl = it.get('explanation', '')
            txt.insert(tk.END, f"Q{i}: {q}\nChosen: {chosen}\nCorrect: {correct}\nExplanation: {expl}\n\n")

    def save_score(self, name, score, total):
        entry = {
            'name': name,
            'score': score,
            'total': total,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        data = []
        try:
            if os.path.exists(SCORES_FILE):
                with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception:
            data = []
        data.append(entry)
        try:
            with open(SCORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo('Saved', 'Score saved to `scores.json`.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save score: {e}')

    def view_scores(self):
        if not os.path.exists(SCORES_FILE):
            messagebox.showinfo('Scores', 'No scores saved yet.')
            return
        try:
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to read scores: {e}')
            return
        text = ''
        for e in data:
            text += f"{e.get('timestamp')} - {e.get('name')}: {e.get('score')}/{e.get('total')}\n"
        popup = tk.Toplevel(self)
        popup.title('Scores')
        txt = tk.Text(popup, wrap='word')
        txt.pack(fill='both', expand=True)
        txt.insert('1.0', text)

    def clear_scores(self):
        if messagebox.askyesno('Clear', 'Clear all saved scores?'):
            try:
                if os.path.exists(SCORES_FILE):
                    os.remove(SCORES_FILE)
                messagebox.showinfo('Cleared', 'Scores cleared.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to clear scores: {e}')

if __name__ == '__main__':
    app = CiscoAdminGame()
    app.mainloop()
