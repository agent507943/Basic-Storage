import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import random
import os
import ipaddress
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
SCORES_FILE = os.path.join(BASE_DIR, "scores.json")
REVIEW_FILE = os.path.join(BASE_DIR, "review_list.json")

QUESTION_COUNT_CHOICES = [10, 15, 20, 25]
DEFAULT_QUESTION_COUNT = 20

default_settings = {"sound_enabled": True}
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


def load_questions():
    """Load the merged routing question bank."""
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [q for q in data if isinstance(q, dict)]
    except Exception:
        pass
    return []


QUESTIONS = load_questions()

DIFFICULTIES = ["easy", "medium", "hard"]
QUESTIONS_BY_DIFF = {d: [q for q in QUESTIONS if q.get("difficulty") == d] for d in DIFFICULTIES}

ROUTE_LAB_ROUTES = [
    {
        "prefix": "10.10.1.128/25",
        "protocol": "Static",
        "ad": 1,
        "metric": 0,
        "next_hop": "R1",
        "interface": "Gi0/0",
        "path": ["Edge", "R1", "LAN-A"],
        "color": "#ff7043",
    },
    {
        "prefix": "10.10.1.0/24",
        "protocol": "OSPF",
        "ad": 110,
        "metric": 20,
        "next_hop": "R2",
        "interface": "Gi0/1",
        "path": ["Edge", "R2", "LAN-B"],
        "color": "#42a5f5",
    },
    {
        "prefix": "10.10.0.0/16",
        "protocol": "EIGRP",
        "ad": 90,
        "metric": 30720,
        "next_hop": "R3",
        "interface": "Gi0/2",
        "path": ["Edge", "R3", "LAN-C"],
        "color": "#66bb6a",
    },
    {
        "prefix": "10.0.0.0/8",
        "protocol": "BGP",
        "ad": 20,
        "metric": 100,
        "next_hop": "ISP",
        "interface": "Gi0/3",
        "path": ["Edge", "ISP", "Internet"],
        "color": "#ab47bc",
    },
    {
        "prefix": "0.0.0.0/0",
        "protocol": "BGP Default",
        "ad": 200,
        "metric": 200,
        "next_hop": "Backup ISP",
        "interface": "Gi0/4",
        "path": ["Edge", "Backup ISP", "Internet"],
        "color": "#8d6e63",
    },
]

ROUTE_LAB_NODES = {
    "Edge": (155, 175),
    "R1": (315, 95),
    "R2": (315, 175),
    "R3": (315, 255),
    "ISP": (500, 115),
    "Backup ISP": (500, 230),
    "LAN-A": (680, 95),
    "LAN-B": (680, 175),
    "LAN-C": (680, 255),
    "Internet": (695, 165),
}

ROUTE_LAB_SCENARIOS = {
    "LPM default test": {
        "destination": "10.10.1.130",
        "focus": ["10.10.1.128/25", "10.10.1.0/24", "10.10.0.0/16", "10.0.0.0/8", "0.0.0.0/0"],
    },
    "BGP exit test": {
        "destination": "10.44.5.9",
        "focus": ["10.0.0.0/8", "0.0.0.0/0"],
    },
    "Summary route test": {
        "destination": "10.10.3.14",
        "focus": ["10.10.0.0/16", "10.0.0.0/8", "0.0.0.0/0"],
    },
}

OSPF_LAB_NODES = {
    "R1": (85, 120),
    "R2 ABR": (215, 120),
    "R3": (85, 225),
    "R4": (340, 120),
    "R5": (465, 120),
    "LAN0": (150, 55),
    "LAN1": (403, 55),
    "ASBR": (465, 225),
}

OSPF_LAB_SCENARIOS = {
    "Backbone and ABR": {
        "summary": "R2 is the ABR between Area 0 and Area 1. Type 3 summaries cross the boundary; Type 1 stays local.",
        "highlight": ["R1", "R2 ABR", "R4", "R5", "LAN0", "LAN1"],
        "roles": {
            "R1": "Internal router",
            "R2 ABR": "ABR",
            "R3": "Internal router",
            "R4": "Internal router",
            "R5": "Internal router",
        },
        "lsa_rows": [
            ("Type 1", "Area 0", "R1 / R2", "Router links stay inside the area."),
            ("Type 2", "Area 0", "LAN0 DR", "Multi-access network information."),
            ("Type 3", "Area 1", "R2 ABR", "Summary routes are injected into the other area."),
            ("Type 5", "External", "ASBR", "External routes are blocked in stub-style designs."),
        ],
    },
    "Stub area": {
        "summary": "A stub area blocks Type 5 external LSAs and uses a default route toward the ABR instead.",
        "highlight": ["R2 ABR", "R4", "R5", "LAN1"],
        "roles": {
            "R2 ABR": "ABR / default route source",
            "R4": "Stub area internal router",
            "R5": "Stub area internal router",
        },
        "lsa_rows": [
            ("Type 1", "Area 1", "R4 / R5", "Stub routers still exchange local topology."),
            ("Type 3", "Area 1", "R2 ABR", "Summary routes are still allowed."),
            ("Type 5", "Area 1", "Blocked", "External LSAs are filtered out in a stub area."),
            ("Default", "Area 1", "R2 ABR", "A default route is used instead of external details."),
        ],
    },
    "DR election": {
        "summary": "On a broadcast segment, the router with the highest OSPF priority becomes DR; the next highest becomes BDR.",
        "highlight": ["R1", "R2 ABR", "R3", "LAN0"],
        "roles": {
            "R1": "Priority 1 - DROTHER",
            "R2 ABR": "Priority 100 - DR",
            "R3": "Priority 50 - BDR",
        },
        "lsa_rows": [
            ("DR", "Area 0", "R2 ABR", "Highest priority wins DR on the shared LAN."),
            ("BDR", "Area 0", "R3", "Next highest priority becomes BDR."),
            ("DROTHER", "Area 0", "R1", "Other routers remain DROTHER and do not become DR/BDR."),
            ("Type 2", "Area 0", "LAN0 DR", "The DR originates the network LSA for the shared segment."),
        ],
    },
}


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
                winsound.Beep(600, 120)
                winsound.Beep(800, 120)
                winsound.Beep(900, 150)
            elif kind == "wrong":
                winsound.Beep(450, 150)
                winsound.Beep(300, 150)
                winsound.Beep(200, 200)
            elif kind == "finish":
                winsound.Beep(500, 100)
                winsound.Beep(700, 100)
                winsound.Beep(900, 100)
                winsound.Beep(1100, 150)
                winsound.Beep(900, 100)
                winsound.Beep(700, 100)
                winsound.Beep(500, 200)
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
        self.title("Routing Learning - Protocols, Design & Security")
        self.geometry("820x650")
        self.resizable(False, False)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.study_frame = ttk.Frame(self.nb)
        self.nb.add(self.study_frame, text="Study")
        self._build_study_tab()

        self.lab_frame = ttk.Frame(self.nb)
        self.nb.add(self.lab_frame, text="Route Lab")
        self._build_route_lab_tab()

        self.ospf_frame = ttk.Frame(self.nb)
        self.nb.add(self.ospf_frame, text="OSPF Lab")
        self._build_ospf_lab_tab()

        self.quiz_frame = ttk.Frame(self.nb)
        self.nb.add(self.quiz_frame, text="Quiz Game")
        self._build_quiz_tab()

        self.history_frame = ttk.Frame(self.nb)
        self.nb.add(self.history_frame, text="History")
        self._build_history_tab()

    def _build_study_tab(self):
        lbl = ttk.Label(self.study_frame, text="Study: Routing Guide", font=(None, 16))
        lbl.pack(pady=8)

        self.study_text = scrolledtext.ScrolledText(self.study_frame, wrap=tk.WORD)
        self.study_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        try:
            with open(STUDY_FILE, "r", encoding="utf-8") as sf:
                content = sf.read()
        except Exception:
            content = "Study content not found."
        self.study_text.insert(tk.END, content)
        self.study_text.configure(state=tk.DISABLED)

    def _build_route_lab_tab(self):
        title = ttk.Label(self.lab_frame, text="Route Lab: Longest Prefix Match and Path Selection", font=(None, 15))
        title.pack(pady=(8, 4))

        intro = ttk.Label(
            self.lab_frame,
            text="Enter a destination IP or pick a scenario to see which route wins, why it wins, and which path the packet takes.",
            wraplength=780,
        )
        intro.pack(pady=(0, 8))

        controls = ttk.Frame(self.lab_frame)
        controls.pack(fill=tk.X, padx=10, pady=(0, 8))

        ttk.Label(controls, text="Destination IP:").pack(side=tk.LEFT, padx=(0, 6))
        self.lab_dest_var = tk.StringVar(value="10.10.1.130")
        self.lab_dest_entry = ttk.Entry(controls, textvariable=self.lab_dest_var, width=18)
        self.lab_dest_entry.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(controls, text="Scenario:").pack(side=tk.LEFT, padx=(0, 6))
        self.lab_scenario_var = tk.StringVar(value="LPM default test")
        self.lab_scenario_menu = ttk.OptionMenu(controls, self.lab_scenario_var, "LPM default test", *ROUTE_LAB_SCENARIOS.keys())
        self.lab_scenario_menu.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(controls, text="Load Scenario", command=self.load_route_lab_scenario).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(controls, text="Analyze Route", command=self.analyze_route_lab).pack(side=tk.LEFT, padx=(0, 6))

        main = ttk.Frame(self.lab_frame)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.lab_canvas = tk.Canvas(left, width=520, height=360, bg="#101420", highlightthickness=0)
        self.lab_canvas.pack(fill=tk.BOTH, expand=True)

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Route Analysis", font=(None, 13)).pack(anchor="w", pady=(0, 4))
        self.lab_summary_var = tk.StringVar(value="Choose a scenario and click Analyze Route.")
        ttk.Label(right, textvariable=self.lab_summary_var, wraplength=250, justify="left").pack(anchor="w", pady=(0, 8))

        columns = ("prefix", "protocol", "ad", "metric")
        self.lab_tree = ttk.Treeview(right, columns=columns, show="headings", height=10)
        for col, label, width in (("prefix", "Prefix", 95), ("protocol", "Protocol", 70), ("ad", "AD", 40), ("metric", "Metric", 60)):
            self.lab_tree.heading(col, text=label)
            self.lab_tree.column(col, width=width, anchor="w")
        self.lab_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.lab_detail_var = tk.StringVar(value="Route details will appear here.")
        ttk.Label(right, textvariable=self.lab_detail_var, wraplength=250, justify="left").pack(anchor="w")

        self.lab_dest_entry.bind("<Return>", lambda _event: self.analyze_route_lab())
        self.load_route_lab_scenario()

    def _build_ospf_lab_tab(self):
        title = ttk.Label(self.ospf_frame, text="OSPF Lab: Areas, DR/BDR, and LSA Flow", font=(None, 15))
        title.pack(pady=(8, 4))

        intro = ttk.Label(
            self.ospf_frame,
            text="Pick a scenario to visualize backbone/area boundaries, DR election, and how LSAs move through the topology.",
            wraplength=780,
        )
        intro.pack(pady=(0, 8))

        controls = ttk.Frame(self.ospf_frame)
        controls.pack(fill=tk.X, padx=10, pady=(0, 8))

        ttk.Label(controls, text="Scenario:").pack(side=tk.LEFT, padx=(0, 6))
        self.ospf_scenario_var = tk.StringVar(value="Backbone and ABR")
        self.ospf_scenario_menu = ttk.OptionMenu(controls, self.ospf_scenario_var, "Backbone and ABR", *OSPF_LAB_SCENARIOS.keys())
        self.ospf_scenario_menu.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(controls, text="Analyze OSPF", command=self.analyze_ospf_lab).pack(side=tk.LEFT, padx=(0, 6))

        main = ttk.Frame(self.ospf_frame)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.ospf_canvas = tk.Canvas(left, width=520, height=360, bg="#101420", highlightthickness=0)
        self.ospf_canvas.pack(fill=tk.BOTH, expand=True)

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="OSPF Analysis", font=(None, 13)).pack(anchor="w", pady=(0, 4))
        self.ospf_summary_var = tk.StringVar(value="Choose an OSPF scenario and click Analyze OSPF.")
        ttk.Label(right, textvariable=self.ospf_summary_var, wraplength=250, justify="left").pack(anchor="w", pady=(0, 8))

        self.ospf_tree = ttk.Treeview(right, columns=("lsa", "area", "source", "meaning"), show="headings", height=9)
        for col, label, width in (("lsa", "LSA/Role", 70), ("area", "Area", 50), ("source", "Source", 70), ("meaning", "Meaning", 120)):
            self.ospf_tree.heading(col, text=label)
            self.ospf_tree.column(col, width=width, anchor="w")
        self.ospf_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.ospf_detail_var = tk.StringVar(value="OSPF details will appear here.")
        ttk.Label(right, textvariable=self.ospf_detail_var, wraplength=250, justify="left").pack(anchor="w")

        self.analyze_ospf_lab()

    def _build_quiz_tab(self):
        top_frame = ttk.Frame(self.quiz_frame)
        top_frame.pack(fill=tk.X, pady=6)

        ttk.Label(top_frame, text="Difficulty:").pack(side=tk.LEFT, padx=(8, 0))
        self.diff_var = tk.StringVar(value="easy")
        diff_menu = ttk.OptionMenu(top_frame, self.diff_var, "easy", *DIFFICULTIES)
        diff_menu.pack(side=tk.LEFT)

        ttk.Label(top_frame, text="Questions:").pack(side=tk.LEFT, padx=(12, 0))
        self.qlen_var = tk.IntVar(value=DEFAULT_QUESTION_COUNT)
        qlen_menu = ttk.OptionMenu(top_frame, self.qlen_var, DEFAULT_QUESTION_COUNT, *QUESTION_COUNT_CHOICES)
        qlen_menu.pack(side=tk.LEFT)

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

        self.progressbar = ttk.Progressbar(top_frame, length=200, maximum=DEFAULT_QUESTION_COUNT)
        self.progressbar.pack(side=tk.RIGHT, padx=6)
        self.qcount_var = tk.StringVar(value="0/0")
        ttk.Label(top_frame, textvariable=self.qcount_var).pack(side=tk.RIGHT)

        self.q_frame = ttk.Frame(self.quiz_frame)
        self.q_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.anim_canvas = tk.Canvas(self.q_frame, width=780, height=120, bg=self.cget('bg'), highlightthickness=0)
        self.anim_canvas.pack(pady=(6, 4))

        self.q_label = ttk.Label(self.q_frame, text="Press Start to begin", wraplength=780, font=(None, 14))
        self.q_label.pack(pady=4)

        help_row = ttk.Frame(self.q_frame)
        help_row.pack(fill=tk.X)
        self.help_btn = ttk.Button(help_row, text="\U0001F4A1 Help", command=self.toggle_hint, state="disabled")
        self.help_btn.pack(side=tk.LEFT, padx=4)

        self.hint_frame = ttk.LabelFrame(self.q_frame, text="Hint")
        self.hint_var = tk.StringVar(value="")
        ttk.Label(self.hint_frame, textvariable=self.hint_var, wraplength=760, justify="left").pack(padx=6, pady=4)

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
        self.correct_count = 0

    def _build_history_tab(self):
        lbl = ttk.Label(self.history_frame, text="Score History (last 20)", font=(None, 14))
        lbl.pack(pady=8)
        self.history_list = tk.Listbox(self.history_frame, height=15)
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side=tk.RIGHT, padx=6)
        self.update_history_view()

    def load_route_lab_scenario(self):
        scenario_name = self.lab_scenario_var.get()
        scenario = ROUTE_LAB_SCENARIOS.get(scenario_name)
        if not scenario:
            return
        self.lab_dest_var.set(scenario.get("destination", ""))
        self.analyze_route_lab()

    def _route_lab_matches(self, dest_ip):
        try:
            dest = ipaddress.ip_address(dest_ip)
        except ValueError:
            return None, [], "Invalid destination IP address."

        matches = []
        for route in ROUTE_LAB_ROUTES:
            try:
                network = ipaddress.ip_network(route["prefix"], strict=False)
            except ValueError:
                continue
            if dest in network:
                item = dict(route)
                item["network"] = network
                item["prefixlen"] = network.prefixlen
                matches.append(item)

        if not matches:
            return dest, [], "No matching route found. The packet would be dropped unless a suitable default route exists."

        matches.sort(key=lambda r: (-r["prefixlen"], r["ad"], r["metric"]))
        return dest, matches, ""

    def _draw_node(self, canvas, x, y, label, fill="#1e2633", outline="#7aa2f7", radius=20, text_fill="#f5f7ff"):
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, outline=outline, width=2)
        canvas.create_text(x, y, text=label, fill=text_fill, font=(None, 9, "bold"))

    def _draw_link(self, canvas, start, end, nodes_map, color="#51627a", width=3, dash=None):
        x1, y1 = nodes_map[start]
        x2, y2 = nodes_map[end]
        canvas.create_line(x1, y1, x2, y2, fill=color, width=width, dash=dash)

    def render_route_lab(self, dest_ip, matches, focus_prefixes=None):
        focus_prefixes = focus_prefixes or []
        self.lab_canvas.delete("all")
        self.lab_canvas.create_rectangle(0, 0, 520, 360, fill="#101420", outline="")
        self.lab_canvas.create_text(16, 14, anchor="nw", text=f"Destination: {dest_ip}", fill="#d7e3ff", font=(None, 11, "bold"))

        for route in ROUTE_LAB_ROUTES:
            path = route["path"]
            active = route["prefix"] in focus_prefixes
            line_color = route["color"] if active else "#39485f"
            line_width = 5 if active else 2
            for start, end in zip(path, path[1:]):
                self._draw_link(self.lab_canvas, start, end, ROUTE_LAB_NODES, color=line_color, width=line_width)

        for name, (x, y) in ROUTE_LAB_NODES.items():
            fill = "#233044"
            outline = "#7aa2f7"
            if name == "Edge":
                fill = "#0f5b78"
                outline = "#4dd0e1"
            if name in {"LAN-A", "LAN-B", "LAN-C", "Internet"}:
                fill = "#2a1d35" if name != "Internet" else "#293f2e"
                outline = "#9fa8da" if name != "Internet" else "#81c784"
            self._draw_node(self.lab_canvas, x, y, name, fill=fill, outline=outline, radius=22 if name == "Edge" else 19)

        if matches:
            winner = matches[0]
            self.lab_canvas.create_rectangle(10, 38, 510, 95, fill="#162033", outline="#57b6ff")
            self.lab_canvas.create_text(
                18,
                46,
                anchor="nw",
                text=f"Winning route: {winner['prefix']} via {winner['protocol']}  |  AD {winner['ad']}  |  Metric {winner['metric']}",
                fill="#eff6ff",
                font=(None, 10, "bold"),
                width=480,
            )
            self.lab_canvas.create_text(
                18,
                66,
                anchor="nw",
                text=f"Reason: longest prefix match wins first, then lower administrative distance and metric decide ties.",
                fill="#cfe3ff",
                font=(None, 9),
                width=480,
            )

            for route in matches[:3]:
                path = route["path"]
                for start, end in zip(path, path[1:]):
                    self._draw_link(self.lab_canvas, start, end, ROUTE_LAB_NODES, color=route["color"], width=5)

    def analyze_route_lab(self):
        dest_ip = self.lab_dest_var.get().strip()
        scenario_name = self.lab_scenario_var.get()
        scenario = ROUTE_LAB_SCENARIOS.get(scenario_name, {})
        focus_prefixes = scenario.get("focus", [])
        dest, matches, error_text = self._route_lab_matches(dest_ip)

        for item in self.lab_tree.get_children():
            self.lab_tree.delete(item)

        if dest is None:
            self.lab_summary_var.set(error_text)
            self.lab_detail_var.set("Enter a valid IPv4 address to see route selection.")
            self.render_route_lab(dest_ip, [], focus_prefixes)
            return

        if not matches:
            self.lab_summary_var.set(error_text)
            self.lab_detail_var.set("Only the default route would help here if one existed.")
            self.render_route_lab(dest_ip, [], focus_prefixes)
            return

        winner = matches[0]
        self.lab_summary_var.set(
            f"Best match: {winner['prefix']} via {winner['protocol']} from {winner['next_hop']} on {winner['interface']}."
        )
        self.lab_detail_var.set(
            f"Why it wins: it is the longest matching prefix. If two routes tie on prefix length, lower AD wins; if AD ties, lower metric wins."
        )

        for route in matches:
            self.lab_tree.insert("", tk.END, values=(route["prefix"], route["protocol"], route["ad"], route["metric"]))

        self.render_route_lab(dest_ip, matches, focus_prefixes)

    def analyze_ospf_lab(self):
        scenario_name = self.ospf_scenario_var.get()
        scenario = OSPF_LAB_SCENARIOS.get(scenario_name)
        if not scenario:
            return

        for item in self.ospf_tree.get_children():
            self.ospf_tree.delete(item)

        self.ospf_summary_var.set(scenario["summary"])
        role_lines = [f"{node}: {role}" for node, role in scenario.get("roles", {}).items()]
        self.ospf_detail_var.set("; ".join(role_lines) if role_lines else "Inspect the diagram to see how the area boundary changes the OSPF view.")

        for row in scenario.get("lsa_rows", []):
            self.ospf_tree.insert("", tk.END, values=row)

        self.render_ospf_lab(scenario_name)

    def render_ospf_lab(self, scenario_name):
        scenario = OSPF_LAB_SCENARIOS.get(scenario_name, {})
        highlight = set(scenario.get("highlight", []))
        roles = scenario.get("roles", {})

        canvas = self.ospf_canvas
        canvas.delete("all")
        canvas.create_rectangle(0, 0, 520, 360, fill="#101420", outline="")
        canvas.create_text(16, 14, anchor="nw", text=f"Scenario: {scenario_name}", fill="#d7e3ff", font=(None, 11, "bold"))

        canvas.create_rectangle(25, 35, 250, 320, outline="#4dd0e1", width=2, dash=(4, 2))
        canvas.create_text(36, 42, anchor="nw", text="Area 0", fill="#4dd0e1", font=(None, 10, "bold"))
        canvas.create_rectangle(265, 35, 500, 320, outline="#ab47bc", width=2, dash=(4, 2))
        canvas.create_text(276, 42, anchor="nw", text="Area 1", fill="#ab47bc", font=(None, 10, "bold"))

        link_sets = {
            "Backbone and ABR": [("LAN0", "R1"), ("LAN0", "R2 ABR"), ("LAN0", "R3"), ("R2 ABR", "LAN1"), ("LAN1", "R4"), ("LAN1", "R5"), ("R5", "ASBR")],
            "Stub area": [("LAN0", "R1"), ("LAN0", "R2 ABR"), ("LAN0", "R3"), ("R2 ABR", "LAN1"), ("LAN1", "R4"), ("LAN1", "R5")],
            "DR election": [("LAN0", "R1"), ("LAN0", "R2 ABR"), ("LAN0", "R3"), ("R2 ABR", "LAN1")],
        }

        for start, end in link_sets.get(scenario_name, []):
            active = start in highlight or end in highlight
            color = "#ffd54f" if active else "#44546a"
            width = 4 if active else 2
            self._draw_link(canvas, start, end, OSPF_LAB_NODES, color=color, width=width)

        node_fill_defaults = {
            "R1": ("#233044", "#7aa2f7"),
            "R2 ABR": ("#0f5b78", "#4dd0e1"),
            "R3": ("#233044", "#7aa2f7"),
            "R4": ("#2a1d35", "#ab47bc"),
            "R5": ("#2a1d35", "#ab47bc"),
            "LAN0": ("#173b2e", "#81c784"),
            "LAN1": ("#173b2e", "#81c784"),
            "ASBR": ("#4d2b1f", "#ff8a65"),
        }

        for name, (x, y) in OSPF_LAB_NODES.items():
            fill, outline = node_fill_defaults.get(name, ("#233044", "#7aa2f7"))
            if "DR" in roles.get(name, ""):
                fill, outline = "#b71c1c", "#ff8a80"
            elif "BDR" in roles.get(name, ""):
                fill, outline = "#ff8f00", "#ffe082"
            elif "ABR" in name:
                fill, outline = "#0f5b78", "#4dd0e1"
            if name not in highlight and name not in {"LAN0", "LAN1", "ASBR"}:
                outline = "#607d8b"
            self._draw_node(canvas, x, y, name, fill=fill, outline=outline, radius=21 if "LAN" not in name else 18)
            if name in roles:
                canvas.create_text(x, y + 30, text=roles[name], fill="#d7e3ff", font=(None, 8), width=90)

        if scenario_name == "DR election":
            canvas.create_rectangle(18, 270, 250, 340, fill="#162033", outline="#ffb74d")
            canvas.create_text(28, 278, anchor="nw", text="Election order", fill="#ffcc80", font=(None, 9, "bold"))
            canvas.create_text(28, 297, anchor="nw", text="1) Highest priority = DR\n2) Next highest = BDR\n3) Others = DROTHER", fill="#e8f0ff", font=(None, 9))

        if scenario_name == "Stub area":
            canvas.create_rectangle(260, 270, 505, 340, fill="#162033", outline="#81c784")
            canvas.create_text(270, 278, anchor="nw", text="Stub reminder", fill="#a5d6a7", font=(None, 9, "bold"))
            canvas.create_text(270, 297, anchor="nw", text="Type 5 LSAs are blocked. The ABR injects a default route instead.", fill="#e8f0ff", font=(None, 9), width=220)

    def update_history_view(self):
        self.history_list.delete(0, tk.END)
        scores = load_scores()
        for rec in scores:
            t = rec.get("time", "")
            s = rec.get("score", 0)
            d = rec.get("difficulty", "")
            pct = rec.get("percentage")
            pct_text = f" ({pct:.0f}%)" if pct is not None else ""
            pretty = f"{t} | {d} | {s}{pct_text}"
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
        requested = self.qlen_var.get()
        pool = QUESTIONS_BY_DIFF.get(diff, [])
        if not pool:
            messagebox.showwarning("No questions", f"No questions available for {diff}")
            return
        count = min(requested, len(pool))
        if count < requested:
            messagebox.showinfo(
                "Fewer questions available",
                f"Only {len(pool)} {diff} questions available. Using all of them."
            )
        self.current_questions = random.sample(pool, count)
        self.current_index = 0
        self.score = 0
        self.correct_count = 0
        self.score_var.set(self.score)
        self.progressbar['maximum'] = len(self.current_questions)
        self._show_question()
        self.progressbar['value'] = 1
        self.qcount_var.set(f"1/{len(self.current_questions)}")

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
        self.qcount_var.set(f"{self.current_index + 1}/{len(self.current_questions)}")
        self.hint_frame.pack_forget()
        self.hint_var.set("")
        self.help_btn.state(["!disabled"])
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
            self.correct_count += 1
            self.feedback_var.set("Correct! +10 points")
            try:
                spawn_confetti(390, 15, count=24)
                play_sound('correct')
                self._animate_confetti()
            except Exception:
                pass
        else:
            self.score -= 5
            self.feedback_var.set(f"Wrong. -5 points. Correct: {correct}")
            try:
                spawn_confetti(390, 15, count=12)
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
        self.help_btn.state(["disabled"])
        self.hint_frame.pack_forget()

    def toggle_hint(self):
        if not self.current_questions:
            return
        q = self.current_questions[self.current_index]
        if self.hint_frame.winfo_ismapped():
            self.hint_frame.pack_forget()
        else:
            self.hint_var.set(q.get('hint', 'No hint available for this question.'))
            self.hint_frame.pack(fill=tk.X, pady=(0, 6), before=self.choice_buttons[0])

    def next_question(self):
        self.current_index += 1
        if self.current_index >= len(self.current_questions):
            self._finish_quiz()
            return
        self._show_question()
        self.progressbar['value'] = self.current_index + 1
        self.qcount_var.set(f"{self.current_index + 1}/{len(self.current_questions)}")

    def _finish_quiz(self):
        total = len(self.current_questions)
        percentage = (self.correct_count / total) * 100 if total else 0

        if percentage >= 90:
            message = "\U0001F31F Outstanding! You've mastered routing concepts!"
        elif percentage >= 80:
            message = "\U0001F3AF Excellent work! Strong routing knowledge!"
        elif percentage >= 70:
            message = "\U0001F44D Good job! Keep studying to improve further!"
        elif percentage >= 60:
            message = "\U0001F4DA Not bad! Review the concepts and try again!"
        else:
            message = "\U0001F4AA Keep learning! Practice makes perfect!"

        messagebox.showinfo(
            "Quiz finished",
            f"Final score: {self.score}\nCorrect: {self.correct_count}/{total} ({percentage:.1f}%)\n\n{message}"
        )

        record = {
            "score": self.score,
            "percentage": percentage,
            "difficulty": self.diff_var.get(),
            "time": datetime.now().isoformat()
        }
        save_score_record(record)
        self.update_history_view()
        play_sound('finish')

        if percentage >= 90:
            try:
                spawn_confetti(390, 15, count=60)
                self._animate_confetti()
            except Exception:
                pass

        self.end_quiz()

    def end_quiz(self):
        self.current_questions = []
        self.current_index = 0
        self.score = 0
        self.correct_count = 0
        self.score_var.set(self.score)
        self.q_label.config(text="Press Start to begin")
        for var in self.choices_vars:
            var.set("")
        for btn in self.choice_buttons:
            btn.state(["disabled"])
        self.help_btn.state(["disabled"])
        self.hint_frame.pack_forget()
        self.progressbar['maximum'] = self.qlen_var.get()
        self.progressbar['value'] = 0
        self.qcount_var.set("0/0")
        self.progress_var.set("0/0")

    def start_review(self):
        # load review list and map to actual question objects
        entries = load_review_list()
        if not entries:
            messagebox.showinfo("Review list empty", "No questions in the review list. Answer some questions incorrectly to add them.")
            return
        objs = []
        for ent in entries:
            matches = [q for q in QUESTIONS if q.get('difficulty') == ent.get('difficulty') and q.get('question') == ent.get('question')]
            if matches:
                objs.append(matches[0])
        if not objs:
            messagebox.showinfo("No matches", "No matching questions found for the saved review list.")
            return
        self.current_questions = objs
        self.current_index = 0
        self.score = 0
        self.correct_count = 0
        self.score_var.set(self.score)
        self.progressbar['maximum'] = len(self.current_questions)
        self._show_question()
        self.progressbar['value'] = 1
        self.qcount_var.set(f"1/{len(self.current_questions)}")

    def _clear_review_prompt(self):
        if messagebox.askyesno("Clear Review List", "Clear all saved review questions?"):
            clear_review_list()
            messagebox.showinfo("Cleared", "Review list cleared.")


if __name__ == '__main__':
    app = RoutingLearnApp()
    app.mainloop()
