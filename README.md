Diagnostica: Virtual Medical Case Simulator
Diagnostica: Virtual Medical Case Simulator is an interactive, text-based strategy, simulation, and diagnostic puzzle game designed to challenge your medical knowledge and decision-making skills. Play as a biomedical intern in a high-tech virtual hospital, where each level presents a new patient with unique symptoms. Your goal is to accurately diagnose and treat them while managing limited hospital credits and facing time-bound emergencies.

🎮 Game Objective
Diagnose & Treat: Analyze patient symptoms, order relevant medical tests, interpret results, and select the correct diagnosis and treatment plan.

Manage Credits: Strategically use your hospital credits. Over-testing or incorrect decisions will incur penalties.

Time-Bound Emergencies: In later stages, face critical scenarios that require quick and accurate decisions under time pressure.

Progress Through Levels: Successfully treat patients to unlock more complex cases and advance your virtual career.

✨ Features
Realistic Case Simulations: Engage with patient scenarios inspired by real biomedical parameters (e.g., CBC values, vital signs).

Progressive Difficulty: Start with basic diagnoses (e.g., Anemia, Flu) and advance to mid-level (e.g., Dengue, Cardiac Arrhythmia) and advanced cases (e.g., Septic Shock, Stroke).

Interactive GUI: Built with ipywidgets for an engaging user interface within a Google Colab environment, featuring buttons, dropdowns, and dynamic display outputs.

AI Assistance Hint: Utilize a limited number of AI-powered hints when you need a nudge in the right direction (use them wisely, they cost credits!).

Score and Credit System: Track your performance with points for correct actions and manage your credits to avoid a "game over."

🚀 How to Play
Diagnostica is designed to run in a Google Colab notebook environment.

Open in Google Colab: Copy and paste the entire Python code block for the game into a new Google Colab notebook.

Run the Code Cell: Execute the code cell (click the "Play" button or press Shift + Enter).

Game Interface Appears: The interactive game interface will load below the code cell.

Game Controls:
Start New Game / Next Patient / Advance to Level X: This dynamic button initiates a new game, moves you to the next patient after a successful case, or progresses you to the next difficulty level.

Game Status: Displays your current Credits, Hints remaining, current Level, and Score. A Time Left countdown appears during time-bound emergencies.

Patient Case: Presents the patient's initial symptoms and lists Available Tests with their associated costs.

Game Output: Provides real-time messages, detailed Test Results, and feedback on your diagnostic and treatment actions.

Order Test:

Select a test from the dropdown menu.

Click the "Order Test" button to retrieve results and deduct credits.

Diagnosis:

Type your precise diagnosis into the "Diagnosis" text box.

Click "Diagnose Patient." You must be correct to proceed to treatment.

Treatment:

Once a correct diagnosis is made, the "Treatment" text box and button become active.

Enter your proposed treatment.

Click "Administer Treatment."

Use Hint: Click this button to receive an AI-assisted hint. Remember, hints are limited and consume credits.

💻 Technical Stack (Google Colab Compatible)
ipywidgets: For building the interactive graphical user interface.

IPython.display: For managing output and interactivity in the notebook.

pandas: (Included for data handling, though current implementation uses Python dictionaries for simplicity and directness in this prototype).

random, time, threading: For core gameplay mechanics, patient selection, and time management.

🧠 Sample Levels
Basic Diagnosis: Anaemia, Flu, Dehydration

Mid-level: Dengue, Cardiac Arrhythmia, Diabetes

Advanced: Septic Shock, Stroke, Metabolic Disorders

📈 Future Enhancements
Fuzzy Matching for Inputs: Implement more forgiving text matching for diagnosis and treatment.

Expanded Patient Database: Add a wider variety of cases and patient data.

Visual Enhancements: Integrate simple graphics or medical icons.

Comprehensive Tutorial: An in-game guide for new players.

Progress Saving: Functionality to save and load game progress.

Good luck, Intern! The virtual patients are counting on you!
