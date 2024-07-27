import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
import random
import time
import json
import os


# We start with Fetching questions from the Open Trivia Database API
def fetch_questions(amount=10, category=9, difficulty='medium', qtype='multiple'):
   url = f"https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={qtype}"
   try:
       response = requests.get(url)
       response.raise_for_status()
       return response.json().get('results', [])
   except requests.RequestException as e:
       messagebox.showerror("Error", f"Failed to fetch questions: {e}")
       return []


# Save high scores to a file
def save_high_scores(scores):
   with open('high_scores.json', 'w') as file:
       json.dump(scores, file)


# Load high scores from a file
def load_high_scores():
   if os.path.exists('high_scores.json'):
       with open('high_scores.json', 'r') as file:
           return json.load(file)
   return []


# Show high scores
def show_high_scores():
   global high_scores
   high_scores_text = "\n".join([f"{i+1}. {score['name']} - {score['score']}" for i, score in enumerate(high_scores)])
   messagebox.showinfo("High Scores", high_scores_text)


# Reset high scores
def reset_high_scores():
   global high_scores
   high_scores = []
   save_high_scores(high_scores)
   messagebox.showinfo("High Scores", "High scores have been reset.")


# Update the timer
def update_timer():
   global start_time, score_multiplier, quiz_active
   if not quiz_active:
       return
   elapsed_time = time.time() - start_time
   remaining_time = 20 - int(elapsed_time)
   if remaining_time >= 0:
       timer_label.config(text=f"Time left: {remaining_time}s")
       root.after(1000, update_timer)
   else:
       
       check_answer(time_up=True)


# Check the answer
def check_answer(time_up=False):
   global score, score_multiplier, quiz_active
   if not quiz_active:
       return
   if not time_up:
       selected_option = options.get()
       selected_text = option_buttons[int(selected_option)].cget("text")
       if selected_text == correct_answer:
           score += score_multiplier
           score_multiplier += 1
           messagebox.showinfo("Result", "Correct!", icon='info')
       else:
           score_multiplier = 1
           messagebox.showinfo("Result", f"Incorrect! The correct answer is {correct_answer}.", icon='error')
   next_question()


# Show the final score
def show_score():
   global score, high_scores, quiz_active
   quiz_active = False
   messagebox.showinfo("Your Quiz is Over", f"You Have Answered {score} out of {len(questions)}")
   name = simpledialog.askstring("High Scores", "Please Enter your name for the high score list:")
   if name:
       high_scores.append({"name": name, "score": score})
       high_scores.sort(key=lambda x: x["score"], reverse=True)
       high_scores = high_scores[:5]
       save_high_scores(high_scores)
       show_high_scores()


# Load the next question
def next_question():
   global question_index, start_time, correct_answer, score, quiz_active
   if not quiz_active:
       return
   if question_index < len(questions):
       q = questions[question_index]
       question_label.config(text=q["question"])
       choices = q["incorrect_answers"] + [q["correct_answer"]]
       random.shuffle(choices)
       for i, choice in enumerate(choices):
           option_buttons[i].config(text=choice)
       correct_answer = q["correct_answer"]
       question_index += 1
       start_time = time.time()
       score_multiplier_label.config(text=f"Score Multiplier: x{score_multiplier}")
       update_timer()
   else:
       show_score()


# Start quiz with selected category and difficulty
def start_quiz():
   global questions, score, question_index, score_multiplier, quiz_active
   selected_category_name = category_var.get()
   category_id = categories[selected_category_name]
   difficulty = difficulty_var.get()
   questions = fetch_questions(amount=10, category=category_id, difficulty=difficulty)
   if questions:
       score = 0
       question_index = 0
       score_multiplier = 1
       quiz_active = True
       next_question()
   else:
       messagebox.showerror("Error", "Failed to load questions. Please try again.")


# Reset the quiz
def reset_quiz():
   global score, question_index, questions, score_multiplier, quiz_active
   score = 0
   question_index = 0
   questions = []
   score_multiplier = 1
   quiz_active = False
   question_label.config(text="")
   for btn in option_buttons:
       btn.config(text="")
   timer_label.config(text="Time left: 20s")
   score_multiplier_label.config(text="Score Multiplier: x1")


# Initialize global variables
score = 0
question_index = 0
questions = []
high_scores = load_high_scores()
score_multiplier = 1
quiz_active = False


# Set up the Tkinter window
root = tk.Tk()
root.title("Quiz Game - The Pycodes")
root.geometry("500x660")


menu = tk.Menu(root)
root.config(menu=menu)
high_score_menu = tk.Menu(menu)
menu.add_cascade(label="High Scores", menu=high_score_menu)
high_score_menu.add_command(label="View High Scores", command=show_high_scores)
high_score_menu.add_command(label="Reset High Scores", command=reset_high_scores)


timer_label = tk.Label(root, text="Time left: 20s", font=("Helvetica", 14))
timer_label.pack(pady=20)


question_label = tk.Label(root, text="", wraplength=400, font=("Helvetica", 16))
question_label.pack(pady=20)


options = tk.StringVar()
option_buttons = []
for i in range(4):
   btn = tk.Radiobutton(root, text="", variable=options, value=i, font=("Helvetica", 14))
   btn.pack(anchor="w")
   option_buttons.append(btn)


submit_button = tk.Button(root, text="Submit", command=lambda: check_answer(time_up=False), font=("Helvetica", 14))
submit_button.pack(pady=20)


score_multiplier_label = tk.Label(root, text="Score Multiplier: x1", font=("Helvetica", 14))
score_multiplier_label.pack(pady=20)


category_label = tk.Label(root, text="Select Category:", font=("Helvetica", 14))
category_label.pack(pady=10)
categories = {
   "General Knowledge": 9,
   "Science & Nature": 17,
   "Sports": 21,
   "Geography": 22,
   "History": 23,
   "Art": 25,
   "Celebrities": 26
}
category_var = tk.StringVar(value="General Knowledge")
category_menu = ttk.Combobox(root, textvariable=category_var, values=list(categories.keys()), state="readonly")
category_menu.pack(pady=10)


difficulty_label = tk.Label(root, text="Select Difficulty:", font=("Helvetica", 14))
difficulty_label.pack(pady=10)
difficulties = ["easy", "medium", "hard"]
difficulty_var = tk.StringVar(value="medium")
difficulty_menu = ttk.Combobox(root, textvariable=difficulty_var, values=difficulties, state="readonly")
difficulty_menu.pack(pady=10)


# Now We Create a frame for the start and stop buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)


start_button = tk.Button(button_frame, text="Start Quiz", command=start_quiz, font=("Helvetica", 14))
start_button.pack(side="left", padx=10)


reset_button = tk.Button(button_frame, text="Reset Quiz", command=reset_quiz, font=("Helvetica", 14))
reset_button.pack(side="left", padx=10)


root.mainloop()
