import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import re
import os
import random
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_FILE = os.path.join(BASE_DIR, 'questions.json')
STUDY_FILE = os.path.join(BASE_DIR, 'study_content.md')
SCORES_FILE = os.path.join(BASE_DIR, 'scores.json')
LABS_FILE = os.path.join(BASE_DIR, 'labs.json')
SCENARIOS_FILE = os.path.join(BASE_DIR, 'scenarios.json')

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
        # Buttons for opening lab documentation
        btn_frame = ttk.Frame(right)
        btn_frame.pack(anchor='w', pady=(4,0))
        ttk.Button(btn_frame, text='Open Lab Markdown (.md)', command=self.open_lab_markdown).pack(side='left', padx=(0,4))
        ttk.Button(btn_frame, text='Open Lab HTML (.html)', command=self.open_lab_html).pack(side='left')
        # Diagram canvas
        self.lab_canvas = tk.Canvas(right, height=200, bg='white')
        self.lab_canvas.pack(fill='x', pady=(6,4))
        self.lab_text = tk.Text(right, height=8, wrap='word')
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

        # Scenario Lookup tab - searchable scenario repository
        scenarios_frame = ttk.Frame(notebook)
        notebook.add(scenarios_frame, text='Scenario Lookup')
        top_s = ttk.Frame(scenarios_frame)
        top_s.pack(fill='x', padx=6, pady=(6,2))
        ttk.Label(top_s, text='Search Scenarios:').pack(side='left')
        self.scenario_search_var = tk.StringVar()
        self.scenario_search_entry = ttk.Entry(top_s, textvariable=self.scenario_search_var, width=50)
        self.scenario_search_entry.pack(side='left', padx=(6,4))
        ttk.Button(top_s, text='Find', command=self.search_scenarios).pack(side='left')
        ttk.Button(top_s, text='Clear', command=lambda: self.populate_scenarios_list(self.scenarios)).pack(side='left', padx=4)
        ttk.Label(top_s, text='Difficulty:').pack(side='left', padx=(12,4))
        self.scenario_diff_var = tk.StringVar(value='all')
        ttk.Combobox(top_s, textvariable=self.scenario_diff_var, values=['all','beginner','intermediate','advanced'], width=12).pack(side='left')
        self.scenario_search_entry.bind('<Return>', lambda e: self.search_scenarios())

        main_s = ttk.Frame(scenarios_frame)
        main_s.pack(fill='both', expand=True, padx=6, pady=6)
        left_s = ttk.Frame(main_s)
        left_s.pack(side='left', fill='y')
        ttk.Label(left_s, text='Scenarios').pack()
        self.scenarios_listbox = tk.Listbox(left_s, width=40, height=20)
        self.scenarios_listbox.pack(fill='y')
        self.scenarios_listbox.bind('<<ListboxSelect>>', lambda e: self.show_selected_scenario())

        right_s = ttk.Frame(main_s)
        right_s.pack(side='left', fill='both', expand=True, padx=(8,0))
        self.scenario_title = ttk.Label(right_s, text='Select a scenario', font=('Segoe UI', 12, 'bold'))
        self.scenario_title.pack(anchor='w')
        self.scenario_text = tk.Text(right_s, wrap='word')
        self.scenario_text.pack(fill='both', expand=True, pady=(6,0))
        ttk.Button(right_s, text='Copy Config to Clipboard', command=self.copy_scenario_config).pack(pady=6)

        # load scenarios
        self.scenarios = self.load_scenarios()
        self.populate_scenarios_list(self.scenarios)

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

    def load_scenarios(self):
        if not os.path.exists(SCENARIOS_FILE):
            return []
        try:
            with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('scenarios', [])
        except Exception:
            return []

    def populate_scenarios_list(self, scenarios):
        self.scenarios_listbox.delete(0, tk.END)
        for s in scenarios:
            title = f"[{s.get('difficulty','?')}] {s.get('title') }"
            self.scenarios_listbox.insert(tk.END, title)

    def search_scenarios(self):
        query = (self.scenario_search_var.get() or '').strip().lower()
        diff = (self.scenario_diff_var.get() or 'all').lower()
        results = []
        for s in self.scenarios:
            if diff != 'all' and s.get('difficulty','').lower() != diff:
                continue
            hay = ' '.join([
                s.get('title',''), s.get('summary',''), s.get('scenario_description',''), s.get('full_config_snippet','')
            ]).lower()
            # also search within steps and commands
            for st in s.get('steps',[]):
                hay += ' ' + ' '.join([str(x).lower() for x in st.get('commands',[])])
                hay += ' ' + (st.get('title','') or '').lower()
            if not query or query in hay:
                results.append(s)
        if not results:
            messagebox.showinfo('Search Results', f'No scenarios match "{query}" with difficulty {diff}.')
        self.populate_scenarios_list(results)
        # temporarily store last search results to map listbox index
        self._last_scenario_results = results

    def show_selected_scenario(self):
        sel = self.scenarios_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        # if a search was done, use results mapping; otherwise use full list
        results = getattr(self, '_last_scenario_results', None)
        if results is None:
            results = self.scenarios
        if idx >= len(results):
            return
        s = results[idx]
        self.render_scenario_details(s)

    def render_scenario_details(self, s):
        self.scenario_title.config(text=s.get('title',''))
        self.scenario_text.delete('1.0', tk.END)
        out = []
        out.append(f"Difficulty: {s.get('difficulty','')}")
        out.append('\nSummary:\n' + s.get('summary',''))
        if s.get('prerequisites'):
            out.append('\nPrerequisites:\n' + '\n'.join(['- '+p for p in s.get('prerequisites',[])]))
        if s.get('scenario_description'):
            out.append('\nScenario Description:\n' + s.get('scenario_description'))
        if s.get('objectives'):
            out.append('\nObjectives:\n' + '\n'.join(['- '+o for o in s.get('objectives',[])]))
        if s.get('steps'):
            out.append('\nSteps:')
            for st in s.get('steps',[]):
                out.append(f"\nStep {st.get('step','?')}: {st.get('title','')}")
                if st.get('commands'):
                    out.append('Commands:')
                    for c in st.get('commands',[]):
                        out.append('  ' + c)
                if st.get('notes'):
                    out.append('Notes: ' + st.get('notes'))
        if s.get('full_config_snippet'):
            out.append('\nFull Configuration Snippet:\n' + s.get('full_config_snippet'))
        self.scenario_text.insert(tk.END, '\n'.join(out))
        # store last selected scenario for copy
        self._last_selected_scenario = s

    def copy_scenario_config(self):
        s = getattr(self, '_last_selected_scenario', None)
        if not s:
            messagebox.showwarning('No selection', 'Select a scenario first')
            return
        cfg = s.get('full_config_snippet','')
        if not cfg:
            messagebox.showinfo('No Config', 'Selected scenario has no full config snippet to copy.')
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(cfg)
            messagebox.showinfo('Copied', 'Configuration snippet copied to clipboard')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to copy to clipboard: {e}')

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
        # ensure markdown doc exists and open it
        try:
            self.open_lab_markdown()
        except Exception:
            pass
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
        # draw diagram if available
        self.lab_canvas.delete('all')
        diagram = self.current_lab.get('diagram')
        if diagram:
            self.draw_lab_diagram(diagram)

    def submit_lab_command(self):
        if not hasattr(self, 'current_lab'):
            messagebox.showwarning('No Lab', 'Start a lab first')
            return
        steps = self.current_lab.get('steps', [])
        step = steps[self.lab_step]
        entered = self.lab_cmd_entry.get().strip()
        expected = step.get('expected', [])
        ok = False
        # check simulated responses first (ping/nslookup etc.)
        sim = self.current_lab.get('simulated', {})
        for pat,res in sim.items():
            # support regex keys (prefix re:), otherwise exact/normalized match
            if pat.startswith('re:'):
                if re.search(pat[3:], entered, re.I):
                    self.lab_output.insert(tk.END, f"{res}\n")
            else:
                if entered.lower() == pat.lower():
                    self.lab_output.insert(tk.END, f"{res}\n")
        # normalize and match expected patterns (support regex with re:)
        def norm(s):
            return re.sub(r'\s+', ' ', (s or '').strip().lower())
        for e in expected:
            if isinstance(e, str) and e.startswith('re:'):
                try:
                    if re.search(e[3:], entered, re.I):
                        ok = True
                        break
                except re.error:
                    pass
            else:
                if norm(e) == norm(entered) or norm(e) in norm(entered) or norm(entered) in norm(e):
                    ok = True
                    break
        if ok:
            out = step.get('success_output', 'Command accepted.')
            self.lab_output.insert(tk.END, out + '\n')
            self.lab_step += 1
            self.after(300, self.show_lab_step)
        else:
            # if no match, provide helpful hint showing normalized expected patterns
            hints = [ (('re:' in e) and e) or re.sub(r'\s+', ' ', e.strip()) for e in expected ]
            self.lab_output.insert(tk.END, f"Incorrect command. Expected one of: {hints}\n")

    def draw_lab_diagram(self, diagram):
        # simple renderer: draw nodes as rectangles with labels and straight links
        nodes = {n['id']: n for n in diagram.get('nodes', [])}
        # draw links
        for a,b in diagram.get('links', []):
            na = nodes.get(a)
            nb = nodes.get(b)
            if not na or not nb:
                continue
            x1,y1 = na.get('x'), na.get('y')
            x2,y2 = nb.get('x'), nb.get('y')
            self.lab_canvas.create_line(x1+40, y1+20, x2+40, y2+20, fill='black', width=2)
        # draw nodes on top
        for n in diagram.get('nodes', []):
            x = n.get('x', 50)
            y = n.get('y', 20)
            w = 100
            h = 36
            self.lab_canvas.create_rectangle(x, y, x+w, y+h, fill='#f0f0f0', outline='black')
            self.lab_canvas.create_text(x+6, y+6, anchor='nw', text=n.get('label',''), font=('Segoe UI', 9))

    def lab_markdown_filename(self, lab):
        # create a safe filename from lab title
        title = lab.get('title','lab').strip().lower()
        safe = re.sub(r'[^a-z0-9_-]+', '_', title)
        docs_dir = os.path.join(BASE_DIR, 'labs_md')
        os.makedirs(docs_dir, exist_ok=True)
        return os.path.join(docs_dir, f"{safe}.md")

    def save_lab_markdown(self, lab):
        """Generate a markdown file for the lab, including a diagram (Mermaid when diagram data exists)."""
        path = self.lab_markdown_filename(lab)
        lines = []
        lines.append(f"# {lab.get('title','Lab')}")
        if lab.get('description'):
            lines.append('\n' + lab.get('description') + '\n')
        # diagram as Mermaid if present
        diagram = lab.get('diagram')
        if diagram:
            lines.append('\n## Diagram\n')
            lines.append('```mermaid')
            lines.append('graph LR')
            # map nodes and produce a more structured network diagram when possible
            id_to_label = {}
            def icon_for_label(labl):
                low = (labl or '').lower()
                if 'internet' in low or 'cloud' in low:
                    return '☁️ '
                if 'firewall' in low or 'fw' in low:
                    return '🛡️ '
                if 'router' in low or 'rtr' in low:
                    return '📡 '
                if 'access point' in low or 'wireless' in low or 'ap' in low:
                    return '📶 '
                if 'switch' in low:
                    return '🔀 '
                if 'server' in low or 'file' in low:
                    return '🗄️ '
                if 'laptop' in low:
                    return '💻 '
                if 'smartphone' in low or 'phone' in low:
                    return '📱 '
                if 'pc' in low or 'desktop' in low:
                    return '🖥️ '
                if 'printer' in low:
                    return '🖨️ '
                return ''

            for n in diagram.get('nodes', []):
                nid = n.get('id') or f"node{len(id_to_label)+1}"
                labl = (n.get('label','') or '').strip()
                icon = icon_for_label(labl)
                display = f"{icon}{labl}" if labl else icon
                display = display.replace('\n','\\n')
                id_to_label[nid] = display
            # synthetic mermaid ids (safe identifiers)
            mermaid_id = {}
            for i, orig in enumerate(id_to_label.keys(), start=1):
                mermaid_id[orig] = f"n{i}"

            # helper to find a node by keyword in its label
            def find_node_keyword(keywords):
                for orig, labl in id_to_label.items():
                    low = (labl or '').lower()
                    for k in keywords:
                        if k in low:
                            return orig
                return None

            internet = find_node_keyword(['internet', 'cloud'])
            firewall = find_node_keyword(['firewall', 'fw'])
            router = find_node_keyword(['router', 'rtr'])
            ap = find_node_keyword(['access point', 'wireless', 'ap'])
            switch = find_node_keyword(['switch'])
            server = find_node_keyword(['server', 'fileserver'])

            # build a structured diagram similar to the attached image
            def mermaid_node(orig):
                return f"{mermaid_id[orig]}[{id_to_label[orig]}]"

            try:
                if internet and firewall:
                    lines.append(f"  {mermaid_id[internet]}(({id_to_label[internet]})) --> {mermaid_id[firewall]}([{id_to_label[firewall]}])")
                    if router:
                        lines.append(f"  {mermaid_id[firewall]} --> {mermaid_id[router]}([{id_to_label[router]}])")
                elif router:
                    lines.append(f"  {mermaid_id[router]}([{id_to_label[router]}])")

                # central router connections
                if router:
                    # server
                    if server:
                        lines.append(f"  {mermaid_id[router]} --> {mermaid_id[server]}([{id_to_label[server]}])")
                    # wireless side
                    if ap:
                        lines.append(f"  {mermaid_id[router]} --> {mermaid_id[ap]}([{id_to_label[ap]}])")
                        # wireless clients (guess by keywords)
                        wireless_clients = []
                        for orig, labl in id_to_label.items():
                            low = (labl or '').lower()
                            if any(k in low for k in ['laptop', 'smartphone', 'phone', 'wireless', 'printer']) and orig != ap:
                                wireless_clients.append(orig)
                        if wireless_clients:
                            lines.append(f"  subgraph Wireless Clients")
                            for w in wireless_clients:
                                lines.append(f"    {mermaid_id[w]}([{id_to_label[w]}])")
                            lines.append(f"  end")
                            # connect AP to clients
                            for w in wireless_clients:
                                lines.append(f"  {mermaid_id[ap]} --> {mermaid_id[w]}")
                    # wired side (switch)
                    if switch:
                        lines.append(f"  {mermaid_id[router]} --> {mermaid_id[switch]}([{id_to_label[switch]}])")
                        wired_clients = []
                        for orig, labl in id_to_label.items():
                            low = (labl or '').lower()
                            if any(k in low for k in ['pc', 'desktop', 'ip phone', 'ip-phone', 'ipphone', 'printer']) and orig != switch:
                                wired_clients.append(orig)
                        if wired_clients:
                            lines.append(f"  subgraph Wired Clients")
                            for w in wired_clients:
                                lines.append(f"    {mermaid_id[w]}([{id_to_label[w]}])")
                            lines.append(f"  end")
                            for w in wired_clients:
                                lines.append(f"  {mermaid_id[switch]} --> {mermaid_id[w]}")

                # if we were unable to detect a router-based structure, fall back to listing nodes and explicit links
                else:
                    # default: create nodes
                    for orig, labl in id_to_label.items():
                        lines.append(f"  {mermaid_id[orig]}[{labl}]")
                    # links
                    for a,b in diagram.get('links', []):
                        if a in mermaid_id and b in mermaid_id:
                            lines.append(f"  {mermaid_id[a]} --> {mermaid_id[b]}")
            except Exception:
                # on any unexpected problem, fall back to simple nodes+links
                for orig, labl in id_to_label.items():
                    lines.append(f"  {mermaid_id[orig]}[{labl}]")
                for a,b in diagram.get('links', []):
                    if a in mermaid_id and b in mermaid_id:
                        lines.append(f"  {mermaid_id[a]} --> {mermaid_id[b]}")

            lines.append('```')

            # If nodes include explicit x/y coordinates, also embed an inline SVG
            # to give a closer visual match to user's reference images.
            has_coords = any(('x' in n and 'y' in n) for n in diagram.get('nodes', []))
            if has_coords:
                # build SVG canvas based on coordinate extents
                nodes_coords = {}
                minx = min(n.get('x', 0) for n in diagram.get('nodes', []))
                miny = min(n.get('y', 0) for n in diagram.get('nodes', []))
                maxx = max(n.get('x', 0) for n in diagram.get('nodes', []))
                maxy = max(n.get('y', 0) for n in diagram.get('nodes', []))
                pad = 40
                width = int(maxx - minx + pad*2 + 200)
                height = int(maxy - miny + pad*2 + 200)
                # compute adjusted positions
                for orig in id_to_label.keys():
                    # find original node entry
                    nent = next((n for n in diagram.get('nodes', []) if n.get('id') == orig), None)
                    if not nent:
                        continue
                    x = int(nent.get('x', 0) - minx + pad + 20)
                    y = int(nent.get('y', 0) - miny + pad + 20)
                    nodes_coords[orig] = (x, y)

                svg_lines = []
                svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
                svg_lines.append('<style> .node { fill:#f8f9fa; stroke:#333; stroke-width:1.5 } .nlabel { font-family:Segoe UI, Arial, sans-serif; font-size:12px; }</style>')
                # draw links first so nodes render on top
                for a,b in diagram.get('links', []):
                    if a in nodes_coords and b in nodes_coords:
                        x1,y1 = nodes_coords[a]
                        x2,y2 = nodes_coords[b]
                        svg_lines.append(f'<line x1="{x1+60}" y1="{y1+20}" x2="{x2+20}" y2="{y2+20}" stroke="#222" stroke-width="2" />')
                # draw nodes
                for orig, lbl in id_to_label.items():
                    pos = nodes_coords.get(orig)
                    if not pos:
                        continue
                    x,y = pos
                    w = 120
                    h = 36
                    rx = 6
                    svg_lines.append(f'<rect class="node" x="{x}" y="{y}" rx="{rx}" ry="{rx}" width="{w}" height="{h}" />')
                    safe_label = (lbl or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                    svg_lines.append(f'<text class="nlabel" x="{x+8}" y="{y+20}">{safe_label}</text>')
                svg_lines.append('</svg>')
                # embed under a visual section
                lines.append('\n## Visual Diagram\n')
                # Insert raw SVG (most Markdown renderers and VS Code preview will render it)
                lines.append('\n'.join(svg_lines))
        # steps and expected
        if lab.get('steps'):
            lines.append('\n## Steps\n')
            for st in lab.get('steps', []):
                lines.append(f"### Step {st.get('step','')}: {st.get('title','')}")
                if st.get('description'):
                    lines.append(st.get('description'))
                if st.get('commands'):
                    lines.append('\n```\n' + '\n'.join(st.get('commands')) + '\n```')
                if st.get('expected'):
                    lines.append('\n**Expected:**')
                    for e in st.get('expected'):
                        lines.append(f"- `{e}`")
        # simulated outputs
        if lab.get('simulated'):
            lines.append('\n## Simulated Outputs\n')
            for k,v in lab.get('simulated', {}).items():
                lines.append(f"- `{k}` => `{v}`")
        # write file
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return path

    def open_lab_markdown(self):
        """Save and open the lab markdown in the system default editor (Windows uses os.startfile)."""
        lab = getattr(self, 'current_lab', None)
        if not lab:
            messagebox.showwarning('No Lab', 'Start a lab first to open its markdown.')
            return
        try:
            path = self.save_lab_markdown(lab)
            # attempt to open with default program (Windows)
            try:
                os.startfile(path)
            except AttributeError:
                # fallback: on non-windows, try open via system
                import webbrowser
                webbrowser.open(path)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to create/open markdown: {e}')

    def open_lab_html(self):
        """Open the lab HTML file in the system default browser."""
        lab = getattr(self, 'current_lab', None)
        if not lab:
            messagebox.showwarning('No Lab', 'Start a lab first to open its HTML file.')
            return
        try:
            # Get the filename base from lab title
            title = lab.get('title', 'lab').strip().lower()
            safe_name = re.sub(r'[^a-z0-9_-]+', '_', title)
            html_path = os.path.join(BASE_DIR, 'labs_md', safe_name + '.html')
            
            if not os.path.exists(html_path):
                messagebox.showwarning('Not Found', f'HTML file not found:\n{html_path}\n\nTry opening the Markdown file first.')
                return
            
            # Open with default browser/program
            try:
                os.startfile(html_path)
            except AttributeError:
                import webbrowser
                webbrowser.open(html_path)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to open HTML file: {e}')

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
