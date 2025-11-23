import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import winsound
import threading

class RoutingLearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Learn Routing - Protocols, Methods & Security")
        self.root.geometry("800x700")
        self.root.configure(bg="#1a1a2e")
        
        # Game state variables
        self.questions = []
        self.current_question = None
        self.current_question_index = 0
        self.score = 0
        self.total_questions = 25  # 25 questions per difficulty level
        self.selected_difficulty = tk.StringVar()
        self.user_answer = tk.StringVar()
        self.quiz_history = []
        
        # Load questions
        self.load_questions()
        
        # Create GUI
        self.create_widgets()
        
    def load_questions(self):
        """Load questions from JSON file"""
        try:
            with open('questions.json', 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "questions.json file not found!")
            self.root.destroy()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in questions.json!")
            self.root.destroy()
            
    def create_widgets(self):
        """Create the GUI elements"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🌐 Learn Routing - Protocols, Methods & Security 🌐",
            font=("Arial", 20, "bold"),
            bg="#1a1a2e",
            fg="#4fc3f7"
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root,
            text="Master routing protocols, security, and network design",
            font=("Arial", 12),
            bg="#1a1a2e",
            fg="#81c784"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(expand=True, fill="both", padx=20)
        
        # Create different screens
        self.create_start_screen()
        self.create_quiz_screen()
        self.create_result_screen()
        
        # Show start screen initially
        self.show_start_screen()
        
    def create_start_screen(self):
        """Create the start screen with difficulty selection"""
        self.start_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        
        # Welcome message
        welcome_label = tk.Label(
            self.start_frame,
            text="Welcome to the Routing Learning App!",
            font=("Arial", 16, "bold"),
            bg="#1a1a2e",
            fg="#fff"
        )
        welcome_label.pack(pady=30)
        
        # Difficulty selection
        difficulty_label = tk.Label(
            self.start_frame,
            text="Select Difficulty Level:",
            font=("Arial", 14),
            bg="#1a1a2e",
            fg="#fff"
        )
        difficulty_label.pack(pady=10)
        
        # Difficulty radio buttons
        difficulties = [
            ("Easy - Basic routing concepts", "easy"),
            ("Medium - Routing protocols and configuration", "medium"),
            ("Hard - Advanced routing and security", "hard")
        ]
        
        for text, value in difficulties:
            rb = tk.Radiobutton(
                self.start_frame,
                text=text,
                variable=self.selected_difficulty,
                value=value,
                font=("Arial", 12),
                bg="#1a1a2e",
                fg="#fff",
                selectcolor="#333",
                activebackground="#1a1a2e",
                activeforeground="#4fc3f7"
            )
            rb.pack(pady=5, anchor="w")
            
        # Set default difficulty
        self.selected_difficulty.set("easy")
        
        # Start button
        start_button = tk.Button(
            self.start_frame,
            text="Start Quiz",
            command=self.start_quiz,
            font=("Arial", 14, "bold"),
            bg="#4fc3f7",
            fg="#1a1a2e",
            padx=30,
            pady=10,
            cursor="hand2"
        )
        start_button.pack(pady=30)
        
    def create_quiz_screen(self):
        """Create the quiz screen"""
        self.quiz_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        
        # Progress frame
        progress_frame = tk.Frame(self.quiz_frame, bg="#1a1a2e")
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Question 1 of 25",
            font=("Arial", 12),
            bg="#1a1a2e",
            fg="#81c784"
        )
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=400,
            mode='determinate',
            maximum=self.total_questions
        )
        self.progress_bar.pack(pady=10)
        
        # Score label
        self.score_label = tk.Label(
            progress_frame,
            text="Score: 0/0",
            font=("Arial", 12, "bold"),
            bg="#1a1a2e",
            fg="#ffb74d"
        )
        self.score_label.pack()
        
        # Question frame
        self.question_frame = tk.Frame(self.quiz_frame, bg="#1a1a2e")
        self.question_frame.pack(fill="both", expand=True, pady=20)
        
        self.question_label = tk.Label(
            self.question_frame,
            text="",
            font=("Arial", 14),
            bg="#1a1a2e",
            fg="#fff",
            wraplength=700,
            justify="center"
        )
        self.question_label.pack(pady=20)
        
        # Answer frame
        self.answer_frame = tk.Frame(self.quiz_frame, bg="#1a1a2e")
        self.answer_frame.pack(pady=20)
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.quiz_frame, bg="#1a1a2e")
        self.buttons_frame.pack(pady=20)
        
        self.submit_button = tk.Button(
            self.buttons_frame,
            text="Submit Answer",
            command=self.submit_answer,
            font=("Arial", 12, "bold"),
            bg="#4caf50",
            fg="#fff",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.submit_button.pack(side="left", padx=10)
        
        self.next_button = tk.Button(
            self.buttons_frame,
            text="Next Question",
            command=self.next_question,
            font=("Arial", 12, "bold"),
            bg="#2196f3",
            fg="#fff",
            padx=20,
            pady=10,
            cursor="hand2",
            state="disabled"
        )
        self.next_button.pack(side="left", padx=10)
        
        # Explanation frame
        self.explanation_frame = tk.Frame(self.quiz_frame, bg="#1a1a2e")
        self.explanation_frame.pack(fill="x", pady=20)
        
        self.explanation_label = tk.Label(
            self.explanation_frame,
            text="",
            font=("Arial", 11),
            bg="#1a1a2e",
            fg="#e0e0e0",
            wraplength=700,
            justify="left"
        )
        self.explanation_label.pack()
        
    def create_result_screen(self):
        """Create the result screen"""
        self.result_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        
        # Results title
        self.result_title = tk.Label(
            self.result_frame,
            text="🎉 Quiz Complete! 🎉",
            font=("Arial", 20, "bold"),
            bg="#1a1a2e",
            fg="#4fc3f7"
        )
        self.result_title.pack(pady=30)
        
        # Score display
        self.final_score_label = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 16),
            bg="#1a1a2e",
            fg="#fff"
        )
        self.final_score_label.pack(pady=20)
        
        # Performance message
        self.performance_label = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 14),
            bg="#1a1a2e",
            fg="#81c784"
        )
        self.performance_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.result_frame, bg="#1a1a2e")
        button_frame.pack(pady=30)
        
        restart_button = tk.Button(
            button_frame,
            text="Take Another Quiz",
            command=self.restart_quiz,
            font=("Arial", 12, "bold"),
            bg="#4fc3f7",
            fg="#1a1a2e",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        restart_button.pack(side="left", padx=10)
        
        quit_button = tk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="#fff",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        quit_button.pack(side="left", padx=10)
        
    def show_start_screen(self):
        """Show the start screen"""
        self.quiz_frame.pack_forget()
        self.result_frame.pack_forget()
        self.start_frame.pack(expand=True, fill="both")
        
    def show_quiz_screen(self):
        """Show the quiz screen"""
        self.start_frame.pack_forget()
        self.result_frame.pack_forget()
        self.quiz_frame.pack(expand=True, fill="both")
        
    def show_result_screen(self):
        """Show the result screen"""
        self.start_frame.pack_forget()
        self.quiz_frame.pack_forget()
        self.result_frame.pack(expand=True, fill="both")
        
    def start_quiz(self):
        """Start the quiz with selected difficulty"""
        if not self.selected_difficulty.get():
            messagebox.showwarning("Warning", "Please select a difficulty level!")
            return
            
        # Reset game state
        self.score = 0
        self.current_question_index = 0
        self.quiz_history = []
        
        # Filter questions by difficulty
        difficulty = self.selected_difficulty.get()
        filtered_questions = [q for q in self.questions if q['difficulty'] == difficulty]
        
        if len(filtered_questions) < self.total_questions:
            messagebox.showwarning(
                "Warning", 
                f"Not enough {difficulty} questions available. Using all available questions."
            )
            self.total_questions = len(filtered_questions)
        
        # Select random questions
        self.current_questions = random.sample(filtered_questions, min(self.total_questions, len(filtered_questions)))
        
        # Update progress bar maximum
        self.progress_bar.config(maximum=len(self.current_questions))
        
        # Show quiz screen and load first question
        self.show_quiz_screen()
        self.load_question()
        
    def load_question(self):
        """Load the current question"""
        if self.current_question_index >= len(self.current_questions):
            self.show_results()
            return
            
        self.current_question = self.current_questions[self.current_question_index]
        
        # Update progress
        self.progress_label.config(
            text=f"Question {self.current_question_index + 1} of {len(self.current_questions)}"
        )
        self.progress_bar.config(value=self.current_question_index)
        self.score_label.config(text=f"Score: {self.score}/{self.current_question_index}")
        
        # Display question
        self.question_label.config(text=self.current_question['question'])
        
        # Clear previous answer widgets
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
            
        # Create answer radio buttons
        self.user_answer.set("")
        for choice in self.current_question['choices']:
            rb = tk.Radiobutton(
                self.answer_frame,
                text=choice,
                variable=self.user_answer,
                value=choice,
                font=("Arial", 11),
                bg="#1a1a2e",
                fg="#fff",
                selectcolor="#333",
                activebackground="#1a1a2e",
                activeforeground="#4fc3f7",
                wraplength=600,
                justify="left"
            )
            rb.pack(anchor="w", pady=5, padx=20)
            
        # Reset button states
        self.submit_button.config(state="normal")
        self.next_button.config(state="disabled")
        
        # Clear explanation
        self.explanation_label.config(text="")
        
    def submit_answer(self):
        """Submit the current answer"""
        if not self.user_answer.get():
            messagebox.showwarning("Warning", "Please select an answer!")
            return
            
        # Check if answer is correct
        is_correct = self.user_answer.get() == self.current_question['answer']
        
        if is_correct:
            self.score += 1
            self.play_routing_success_sound()
            result_text = "✅ Correct!"
            result_color = "#4caf50"
        else:
            self.play_routing_error_sound()
            result_text = f"❌ Incorrect! The correct answer is: {self.current_question['answer']}"
            result_color = "#f44336"
            
        # Store in history
        self.quiz_history.append({
            'question': self.current_question['question'],
            'user_answer': self.user_answer.get(),
            'correct_answer': self.current_question['answer'],
            'is_correct': is_correct
        })
        
        # Show explanation
        explanation_text = f"{result_text}\n\n{self.current_question['explanation']}"
        self.explanation_label.config(text=explanation_text, fg=result_color)
        
        # Update buttons
        self.submit_button.config(state="disabled")
        self.next_button.config(state="normal")
        
        # Update score display
        self.score_label.config(text=f"Score: {self.score}/{self.current_question_index + 1}")
        
    def next_question(self):
        """Move to the next question"""
        self.current_question_index += 1
        self.load_question()
        
    def show_results(self):
        """Show the final results"""
        # Play completion sound
        self.play_routing_completion_sound()
        
        # Calculate percentage
        percentage = (self.score / len(self.current_questions)) * 100
        
        # Update result labels
        self.final_score_label.config(
            text=f"Final Score: {self.score}/{len(self.current_questions)} ({percentage:.1f}%)"
        )
        
        # Performance message
        if percentage >= 90:
            message = "🌟 Outstanding! You've mastered routing concepts!"
            self.create_routing_confetti()
        elif percentage >= 80:
            message = "🎯 Excellent work! You have strong routing knowledge!"
        elif percentage >= 70:
            message = "👍 Good job! Keep studying to improve further!"
        elif percentage >= 60:
            message = "📚 Not bad! Review the concepts and try again!"
        else:
            message = "💪 Keep learning! Practice makes perfect!"
            
        self.performance_label.config(text=message)
        
        # Show result screen
        self.show_result_screen()
        
    def restart_quiz(self):
        """Restart the quiz"""
        self.show_start_screen()
        
    def play_routing_success_sound(self):
        """Play routing success sound - Network convergence tone"""
        def play():
            try:
                # Routing convergence success: 600Hz -> 800Hz -> 900Hz (network stabilization)
                winsound.Beep(600, 120)
                winsound.Beep(800, 120)
                winsound.Beep(900, 150)
            except:
                pass
        threading.Thread(target=play, daemon=True).start()
        
    def play_routing_error_sound(self):
        """Play routing error sound - Network loop/failure tone"""
        def play():
            try:
                # Routing failure: 450Hz -> 300Hz -> 200Hz (network instability)
                winsound.Beep(450, 150)
                winsound.Beep(300, 150)
                winsound.Beep(200, 200)
            except:
                pass
        threading.Thread(target=play, daemon=True).start()
        
    def play_routing_completion_sound(self):
        """Play completion sound - Full network convergence celebration"""
        def play():
            try:
                # Network convergence celebration: ascending then descending pattern
                winsound.Beep(500, 100)
                winsound.Beep(700, 100)
                winsound.Beep(900, 100)
                winsound.Beep(1100, 150)
                winsound.Beep(900, 100)
                winsound.Beep(700, 100)
                winsound.Beep(500, 200)
            except:
                pass
        threading.Thread(target=play, daemon=True).start()
        
    def create_routing_confetti(self):
        """Create confetti effect for excellent performance"""
        def animate_confetti():
            try:
                # Routing-themed colors: blue, green, orange, red, purple, cyan
                colors = ["#2196f3", "#4caf50", "#ff9800", "#f44336", "#9c27b0", "#00bcd4"]
                
                for _ in range(50):
                    x = random.randint(50, 750)
                    y = random.randint(50, 600)
                    color = random.choice(colors)
                    
                    confetti = tk.Label(
                        self.result_frame,
                        text="★",
                        font=("Arial", 16),
                        bg="#1a1a2e",
                        fg=color
                    )
                    confetti.place(x=x, y=y)
                    
                    # Remove after animation
                    self.root.after(3000, confetti.destroy)
                    
            except:
                pass
                
        threading.Thread(target=animate_confetti, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = RoutingLearningApp(root)
    root.mainloop()