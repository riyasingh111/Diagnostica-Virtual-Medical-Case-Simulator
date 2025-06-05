import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import pandas as pd # Included as requested, though main data structure is dict
import random
import time
import threading

# --- Game Global Variables ---
GAME_CREDITS = 1000
HINTS_AVAILABLE = 2
CURRENT_LEVEL = 1 # 1: Basic, 2: Mid-level, 3: Advanced
SCORE = 0
TIME_LIMIT_SECONDS = 0
START_TIME = 0
CURRENT_PATIENT = None
GAME_STATE = "not_started" # "not_started", "playing", "level_complete", "game_over"

# Patient pools for the current game session, populated at start_game
remaining_basic_patients = []
remaining_mid_patients = []
remaining_advanced_patients = []


# --- Patient Data ---
# Structure for each patient case:
# {
#   'id': unique ID for the patient,
#   'theme': 'Blood Disorders' / 'Cardiology' / 'Neurology' / 'Pathology Sim Lab',
#   'difficulty': 'Basic' / 'Mid-level' / 'Advanced',
#   'symptoms': "String describing initial symptoms presented by the patient.",
#   'correct_diagnosis': "The precise medical diagnosis (string).",
#   'correct_treatment': "The correct treatment plan or medication (string).",
#   'tests_available': ['CBC', 'MRI', 'ECG', 'Ultrasound', ...], # List of tests that can be ordered
#   'test_results': {
#       'Test Name': "Formatted string of results, e.g., 'CBC: WBC 3.5, RBC 4.0, HGB 10.0...'",
#       'Another Test Name': "Detailed results for another test."
#   },
#   'test_costs': {
#       'Test Name': cost_integer, # Cost in credits for ordering this test
#       ...
#   },
#   'over_testing_penalty_per_test': 50, # Credits lost if a test is ordered and the overall diagnosis/treatment is wrong
#   'time_bound': False, # True if this is a time-sensitive emergency
#   'time_limit_seconds': 0, # Time limit in seconds if time_bound is True
#   'hint': "AI assistance hint for this specific patient's case."
# }

PATIENT_DATA = [
    {
        'id': 'P001',
        'theme': 'Blood Disorders',
        'difficulty': 'Basic',
        'symptoms': "A 45-year-old female presents with persistent fatigue, dizziness, and pallor. She reports feeling short of breath even with mild exertion.",
        'correct_diagnosis': "Iron Deficiency Anemia",
        'correct_treatment': "Oral Iron Supplements",
        'tests_available': ['CBC', 'Ferritin Level', 'Iron Studies', 'Blood Smear'],
        'test_results': {
            'CBC': "WBC: 7.2 x10^9/L (Normal), RBC: 3.5 x10^12/L (Low), HGB: 9.8 g/dL (Low), HCT: 30% (Low), PLT: 250 x10^9/L (Normal), MCV: 70 fL (Low)",
            'Ferritin Level': "10 ng/mL (Low)",
            'Iron Studies': "Serum Iron: 30 ug/dL (Low), TIBC: 450 ug/dL (High), Transferrin Saturation: 7% (Low)",
            'Blood Smear': "Microcytic, hypochromic red blood cells observed."
        },
        'test_costs': {
            'CBC': 100, 'Ferritin Level': 150, 'Iron Studies': 200, 'Blood Smear': 80
        },
        'over_testing_penalty_per_test': 50,
        'time_bound': False,
        'time_limit_seconds': 0,
        'hint': "Consider common nutritional deficiencies, especially those affecting red blood cell production and size (look at MCV)."
    },
    {
        'id': 'P002',
        'theme': 'Cardiology',
        'difficulty': 'Mid-level',
        'symptoms': "A 68-year-old male complains of sudden onset palpitations, lightheadedness, and an irregular 'racing' heartbeat. He feels generally weak.",
        'correct_diagnosis': "Atrial Fibrillation",
        'correct_treatment': "Anticoagulation and Rate Control Medication",
        'tests_available': ['ECG', 'Echocardiogram', 'Troponin Level', 'Chest X-ray'],
        'test_results': {
            'ECG': "Irregularly irregular rhythm, absence of P waves, narrow QRS complexes.",
            'Echocardiogram': "Normal left ventricular ejection fraction, mild left atrial enlargement. No significant valvular disease.",
            'Troponin Level': "0.02 ng/mL (Normal)",
            'Chest X-ray': "Normal cardiac silhouette, clear lung fields."
        },
        'test_costs': {
            'ECG': 120, 'Echocardiogram': 300, 'Troponin Level': 180, 'Chest X-ray': 90
        },
        'over_testing_penalty_per_test': 60,
        'time_bound': False,
        'time_limit_seconds': 0,
        'hint': "Focus on the heart's electrical activity and the rhythm. The irregular heartbeat is a key clue, particularly the absence of P waves."
    },
    {
        'id': 'P003',
        'theme': 'Neurology',
        'difficulty': 'Advanced',
        'symptoms': "A 72-year-old female is brought in by ambulance with sudden onset weakness on her right side, facial droop, and difficulty speaking. Symptoms began approximately 2 hours ago.",
        'correct_diagnosis': "Ischemic Stroke",
        'correct_treatment': "Thrombolytic Therapy (e.g., Alteplase)",
        'tests_available': ['CT Scan (Brain)', 'MRI (Brain)', 'Carotid Ultrasound', 'Blood Glucose', 'CBC', 'ECG'],
        'test_results': {
            'CT Scan (Brain)': "No evidence of acute hemorrhage. Early ischemic changes noted in left MCA territory.",
            'MRI (Brain)': "Acute infarction evident in left middle cerebral artery territory on diffusion-weighted imaging (DWI).",
            'Carotid Ultrasound': "Mild atherosclerotic plaque in bilateral carotid arteries, no significant stenosis.",
            'Blood Glucose': "110 mg/dL (Normal)",
            'CBC': "WBC: 8.5 x10^9/L (Normal), RBC: 4.8 x10^12/L (Normal), HGB: 14.2 g/dL (Normal), HCT: 42% (Normal), PLT: 280 x10^9/L (Normal)",
            'ECG': "Sinus rhythm, no acute ischemic changes."
        },
        'test_costs': {
            'CT Scan (Brain)': 400, 'MRI (Brain)': 600, 'Carotid Ultrasound': 250, 'Blood Glucose': 50, 'CBC': 100, 'ECG': 120
        },
        'over_testing_penalty_per_test': 100,
        'time_bound': True,
        'time_limit_seconds': 300, # 5 minutes for game purposes
        'hint': "Sudden neurological deficits, especially unilateral, point to a vascular event in the brain. Imaging is crucial to differentiate types, especially ruling out hemorrhage."
    },
    {
        'id': 'P004',
        'theme': 'Pathology Sim Lab',
        'difficulty': 'Mid-level',
        'symptoms': "A 55-year-old male reports increased thirst, frequent urination, and unexplained weight loss over the past few months. He also mentions occasional blurred vision.",
        'correct_diagnosis': "Type 2 Diabetes Mellitus",
        'correct_treatment': "Lifestyle Modifications and Metformin",
        'tests_available': ['Fasting Blood Glucose', 'HbA1c', 'Oral Glucose Tolerance Test (OGTT)', 'Lipid Panel', 'Urinalysis'],
        'test_results': {
            'Fasting Blood Glucose': "180 mg/dL (High)",
            'HbA1c': "8.5% (High)",
            'Oral Glucose Tolerance Test (OGTT)': "2-hour plasma glucose: 250 mg/dL (Diagnostic for Diabetes)",
            'Lipid Panel': "Total Cholesterol: 220 mg/dL (High), LDL: 150 mg/dL (High), HDL: 40 mg/dL (Low), Triglycerides: 200 mg/dL (High)",
            'Urinalysis': "Glucose: Present, Ketones: Negative, Protein: Negative"
        },
        'test_costs': {
            'Fasting Blood Glucose': 80, 'HbA1c': 120, 'Oral Glucose Tolerance Test (OGTT)': 250, 'Lipid Panel': 150, 'Urinalysis': 70
        },
        'over_testing_penalty_per_test': 70,
        'time_bound': False,
        'time_limit_seconds': 0,
        'hint': "The classic triad of polyuria (frequent urination), polydipsia (increased thirst), and unexplained weight loss points to a metabolic disorder related to blood sugar."
    },
    {
        'id': 'P005',
        'theme': 'Blood Disorders',
        'difficulty': 'Mid-level',
        'symptoms': "A 28-year-old male presents with recurrent nosebleeds, easy bruising, and petechiae on his legs. He also reports heavy bleeding after minor cuts.",
        'correct_diagnosis': "Idiopathic Thrombocytopenic Purpura (ITP)",
        'correct_treatment': "Corticosteroids (e.g., Prednisone)",
        'tests_available': ['CBC', 'Peripheral Blood Smear', 'Coagulation Panel (PT/PTT)', 'Bone Marrow Biopsy'],
        'test_results': {
            'CBC': "WBC: 7.5 x10^9/L (Normal), RBC: 4.8 x10^12/L (Normal), HGB: 14.5 g/dL (Normal), HCT: 43% (Normal), PLT: 15 x10^9/L (Critically Low)",
            'Peripheral Blood Smear': "Markedly decreased platelets, some large platelets present. Red blood cells and white blood cells appear normal.",
            'Coagulation Panel (PT/PTT)': "PT: 12.0 seconds (Normal), PTT: 28.0 seconds (Normal)",
            'Bone Marrow Biopsy': "Increased megakaryocytes with immature forms, consistent with increased platelet destruction. (Performed if other tests inconclusive)"
        },
        'test_costs': {
            'CBC': 100, 'Peripheral Blood Smear': 80, 'Coagulation Panel (PT/PTT)': 180, 'Bone Marrow Biopsy': 500
        },
        'over_testing_penalty_per_test': 75,
        'time_bound': False,
        'time_limit_seconds': 0,
        'hint': "Recurrent bleeding and bruising, particularly with petechiae, often indicate an issue with clotting factors or platelet count. The CBC is key here."
    },
    {
        'id': 'P006',
        'theme': 'Cardiology',
        'difficulty': 'Basic',
        'symptoms': "A 58-year-old male presents with sudden onset crushing chest pain radiating to his left arm and jaw. He is also experiencing shortness of breath and sweating.",
        'correct_diagnosis': "Myocardial Infarction (Heart Attack)",
        'correct_treatment': "Emergency Angioplasty and Medications (e.g., Aspirin, Nitroglycerin)",
        'tests_available': ['ECG', 'Troponin Level', 'Cardiac Enzymes', 'Chest X-ray'],
        'test_results': {
            'ECG': "ST-segment elevation in leads II, III, aVF (Inferior MI).",
            'Troponin Level': "5.2 ng/mL (High - indicates cardiac muscle damage)",
            'Cardiac Enzymes': "CK-MB: 150 U/L (High), LDH: 300 U/L (High)",
            'Chest X-ray': "Normal cardiac silhouette, no acute pulmonary pathology."
        },
        'test_costs': {
            'ECG': 120, 'Troponin Level': 180, 'Cardiac Enzymes': 150, 'Chest X-ray': 90
        },
        'over_testing_penalty_per_test': 60,
        'time_bound': False,
        'time_limit_seconds': 0,
        'hint': "Sudden severe chest pain, especially radiating to the arm, is a classic symptom of a cardiac emergency. Look for signs of heart muscle damage in blood tests and ECG."
    },
    {
        'id': 'P007',
        'theme': 'Neurology',
        'difficulty': 'Mid-level',
        'symptoms': "A 32-year-old female presents with a severe, throbbing headache on one side of her head. She reports experiencing flashing lights and zigzag lines in her vision before the headache started. She also has nausea and sensitivity to light and sound.",
        'correct_diagnosis': "Migraine with Aura",
        'correct_treatment': "Triptans and NSAIDs (e.g., Sumatriptan, Ibuprofen)",
        'tests_available': ['CT Scan (Brain)', 'MRI (Brain)', 'Neurological Exam', 'Lumbar Puncture'],
        'test_results': {
            'CT Scan (Brain)': "Normal.",
            'MRI (Brain)': "Normal.",
            'Neurological Exam': "Normal, no focal neurological deficits.",
            'Lumbar Puncture': "Not indicated for primary headache; CSF clear, normal pressure and composition (if performed, typically to rule out other serious conditions)."
        },
        'test_costs': {
            'CT Scan (Brain)': 400, 'MRI (Brain)': 600, 'Neurological Exam': 100, 'Lumbar Puncture': 300
        },
        'over_testing_penalty_per_test': 80,
        'time_bound': False,
        'time_limit_seconds': 0,
        'hint': "The pattern of symptoms, especially the visual disturbances preceding the headache, is highly characteristic of a specific type of headache. Imaging is usually normal for this benign condition."
    },
    {
        'id': 'P008',
        'theme': 'Pathology Sim Lab',
        'difficulty': 'Advanced',
        'symptoms': "A 65-year-old male with a history of pneumonia is admitted with high fever (103°F), confusion, rapid breathing (28 breaths/min), and low blood pressure (80/50 mmHg). His skin is mottled.",
        'correct_diagnosis': "Septic Shock",
        'correct_treatment': "IV Fluids, Broad-spectrum Antibiotics, Vasopressors",
        'tests_available': ['Blood Cultures', 'CBC', 'Lactic Acid', 'Procalcitonin', 'Urinalysis', 'Chest X-ray'],
        'test_results': {
            'Blood Cultures': "Gram-negative rods isolated (e.g., E. coli) from two sites.",
            'CBC': "WBC: 2.5 x10^9/L (Low - indicates severe infection/immunosuppression), HGB: 13.0 g/dL (Normal), PLT: 90 x10^9/L (Low - indicates DIC or organ failure)",
            'Lactic Acid': "6.5 mmol/L (Critically High - indicates hypoperfusion/shock)",
            'Procalcitonin': "15.0 ng/mL (Very High - strong indicator of bacterial sepsis)",
            'Urinalysis': "Leukocyte esterase positive, nitrites positive (consistent with UTI, possible source of infection)",
            'Chest X-ray': "Right lower lobe infiltrate (consistent with pneumonia, possible source of infection)"
        },
        'test_costs': {
            'Blood Cultures': 250, 'CBC': 100, 'Lactic Acid': 150, 'Procalcitonin': 200, 'Urinalysis': 70, 'Chest X-ray': 90
        },
        'over_testing_penalty_per_test': 120,
        'time_bound': True,
        'time_limit_seconds': 240, # 4 minutes for game purposes
        'hint': "This patient is critically ill with signs of widespread infection and organ dysfunction. Look for markers of systemic inflammation and poor tissue perfusion. Time is absolutely critical!"
    }
]

# --- UI Widgets ---
game_output = widgets.Output() # Displays game messages and test results
status_output = widgets.Output() # Displays game credits, hints, level, score, and time
patient_info_output = widgets.Output() # Displays patient symptoms and available tests

# Buttons
start_button = widgets.Button(description="Start New Game", button_style='success',
                              layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))
hint_button = widgets.Button(description="Use Hint (2 left)", button_style='info', disabled=True,
                             layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))
diagnose_button = widgets.Button(description="Diagnose Patient", button_style='primary', disabled=True,
                                 layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))
treat_button = widgets.Button(description="Administer Treatment", button_style='warning', disabled=True,
                              layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))
order_test_button = widgets.Button(description="Order Test", button_style='primary', disabled=True,
                                   layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))

# Dropdowns/Text inputs for actions
test_dropdown = widgets.Dropdown(options=[], description="Order Test:", disabled=True,
                                 layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))
diagnosis_input = widgets.Text(description="Diagnosis:", placeholder="e.g., Iron Deficiency Anemia", disabled=True,
                               layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))
treatment_input = widgets.Text(description="Treatment:", placeholder="e.g., Oral Iron Supplements", disabled=True,
                               layout=widgets.Layout(width='auto', flex='1 1 auto', margin='5px'))

# Main game container
game_container = widgets.VBox([])

# Timer thread for continuous time updates (optional, for visual countdown)
timer_thread = None
timer_stop_event = threading.Event()

# --- Functions ---

def update_status_display():
    """Updates the display showing game credits, hints, level, and time."""
    with status_output:
        clear_output(wait=True)
        html_content = f"""
        <div style="border: 1px solid #ccc; padding: 15px; border-radius: 12px; background-color: #f9f9f9; font-family: 'Inter', sans-serif; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin-top: 0; color: #333; text-align: center; font-size: 1.2em;">Game Status</h3>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <p style="margin: 5px 10px;"><strong>Credits:</strong> <span style="color: green; font-weight: bold;">${GAME_CREDITS}</span></p>
                <p style="margin: 5px 10px;"><strong>Hints:</strong> {HINTS_AVAILABLE} remaining</p>
                <p style="margin: 5px 10px;"><strong>Level:</strong> {CURRENT_LEVEL}</p>
                <p style="margin: 5px 10px;"><strong>Score:</strong> {SCORE}</p>
        """
        if CURRENT_PATIENT and CURRENT_PATIENT['time_bound'] and GAME_STATE == "playing":
            time_elapsed = time.time() - START_TIME
            time_left = max(0, TIME_LIMIT_SECONDS - time_elapsed)
            minutes, seconds = divmod(int(time_left), 60)
            time_color = 'red' if time_left < 60 else 'green'
            html_content += f"<p style='margin: 5px 10px;'><strong>Time Left:</strong> <span style='color: {time_color}; font-weight: bold;'>{minutes:02d}:{seconds:02d}</span></p>"
        html_content += "</div></div>"
        display(HTML(html_content))

def display_patient_info():
    """Displays the current patient's symptoms and available tests."""
    with patient_info_output:
        clear_output(wait=True)
        if CURRENT_PATIENT:
            html_content = f"""
            <div style="border: 1px solid #cce; padding: 15px; border-radius: 12px; background-color: #eef; font-family: 'Inter', sans-serif; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #336; text-align: center; font-size: 1.3em;">Patient Case: {CURRENT_PATIENT['id']} - {CURRENT_PATIENT['theme']} (Difficulty: {CURRENT_PATIENT['difficulty']})</h3>
                <p style="font-size: 1.1em; line-height: 1.5;"><strong>Initial Symptoms:</strong> {CURRENT_PATIENT['symptoms']}</p>
                <div style="margin-top: 15px;">
                    <p style="font-weight: bold; font-size: 1.1em;">Available Tests (Cost):</p>
                    <ul style="list-style-type: none; padding-left: 0;">
                        {''.join([f"<li style='margin-bottom: 5px;'>🔬 {test} <span style='color: #888;'>($<span style='font-weight: bold;'>{CURRENT_PATIENT['test_costs'][test]}</span>)</span></li>" for test in CURRENT_PATIENT['tests_available']])}
                    </ul>
                </div>
                <p style="font-style: italic; color: #555; font-size: 0.9em; margin-top: 15px;">
                    (Hint: Be careful with over-testing! Each unnecessary test will cost you credits if your final diagnosis/treatment is wrong. Focus on relevant tests.)
                </p>
            </div>
            """
            display(HTML(html_content))
            test_dropdown.options = CURRENT_PATIENT['tests_available']
            test_dropdown.value = CURRENT_PATIENT['tests_available'][0] if CURRENT_PATIENT['tests_available'] else None
        else:
            display(HTML("<p style='text-align: center; color: #666;'>No patient loaded. Click 'Start New Game' to begin.</p>"))

def display_message(message, message_type='info'):
    """Displays a message in the game_output area."""
    with game_output:
        clear_output(wait=True)
        color_map = {
            'info': '#3498db',    # Blue
            'success': '#2ecc71', # Green
            'warning': '#f39c12', # Orange
            'error': '#e74c3c'    # Red
        }
        bg_color_map = {
            'info': '#e8f2fa',
            'success': '#e6faed',
            'warning': '#fff5e0',
            'error': '#fce8e8'
        }
        border_color = color_map.get(message_type, '#333')
        background_color = bg_color_map.get(message_type, '#f0f0f0')

        html_content = f"""
        <div style="border: 1px solid {border_color}; padding: 15px; margin-bottom: 10px; border-radius: 12px; background-color: {background_color}; font-family: 'Inter', sans-serif; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <p style="color: {border_color}; margin: 0; font-size: 1.1em;"><strong>{message}</strong></p>
        </div>
        """
        display(HTML(html_content))

def check_time_limit():
    """Checks if time limit has been exceeded for time-bound levels."""
    global GAME_STATE
    if CURRENT_PATIENT and CURRENT_PATIENT['time_bound'] and GAME_STATE == "playing":
        time_elapsed = time.time() - START_TIME
        if time_elapsed >= TIME_LIMIT_SECONDS:
            display_message("Time's up! You failed to diagnose/treat in time.", 'error')
            end_level(False, "Time's up!")
            return True
    return False

def _timer_update_loop():
    """Continuously updates the time display for time-bound levels."""
    while not timer_stop_event.is_set() and GAME_STATE == "playing" and CURRENT_PATIENT and CURRENT_PATIENT['time_bound']:
        update_status_display()
        time.sleep(1) # Update every second
        if check_time_limit():
            timer_stop_event.set() # Stop timer if time runs out
            break


def start_game(b=None):
    """Initializes a new game session."""
    global GAME_CREDITS, HINTS_AVAILABLE, CURRENT_LEVEL, SCORE, GAME_STATE
    global remaining_basic_patients, remaining_mid_patients, remaining_advanced_patients
    global timer_thread, timer_stop_event

    # Stop any previous timer thread
    timer_stop_event.set()
    if timer_thread and timer_thread.is_alive():
        timer_thread.join(timeout=1) # Give it a moment to stop
    timer_stop_event.clear() # Reset for new game

    # Reset game state
    GAME_CREDITS = 1000
    HINTS_AVAILABLE = 2
    CURRENT_LEVEL = 1
    SCORE = 0
    GAME_STATE = "playing"

    # Populate patient pools for current game session (shallow copy to avoid modifying original PATIENT_DATA)
    remaining_basic_patients = [p for p in PATIENT_DATA if p['difficulty'] == 'Basic']
    random.shuffle(remaining_basic_patients)
    remaining_mid_patients = [p for p in PATIENT_DATA if p['difficulty'] == 'Mid-level']
    random.shuffle(remaining_mid_patients)
    remaining_advanced_patients = [p for p in PATIENT_DATA if p['difficulty'] == 'Advanced']
    random.shuffle(remaining_advanced_patients)

    display_message("Welcome to Diagnostica! A new game has started. Good luck, Intern!", 'info')

    # Enable/Disable buttons based on initial state
    start_button.description = "Start New Game" # Reset button text
    start_button.disabled = True # Disable until a level is completed or game over
    hint_button.description = f"Use Hint ({HINTS_AVAILABLE} left)"
    hint_button.disabled = False
    diagnose_button.disabled = False
    treat_button.disabled = True # Treatment disabled until diagnosis is correct
    test_dropdown.disabled = False
    order_test_button.disabled = False
    diagnosis_input.disabled = False
    treatment_input.disabled = True # Treatment input disabled until diagnosis is correct

    load_new_patient()


def load_new_patient():
    """Loads a random patient for the current level."""
    global CURRENT_PATIENT, START_TIME, TIME_LIMIT_SECONDS, GAME_STATE, CURRENT_LEVEL
    global timer_thread, timer_stop_event

    # Disable buttons while loading
    diagnose_button.disabled = False
    treat_button.disabled = True
    test_dropdown.disabled = False
    order_test_button.disabled = False
    diagnosis_input.disabled = False
    treatment_input.disabled = True
    hint_button.disabled = (HINTS_AVAILABLE == 0)

    patient_selected = False
    if CURRENT_LEVEL == 1 and remaining_basic_patients:
        CURRENT_PATIENT = remaining_basic_patients.pop(0) # Get first, remove
        patient_selected = True
    elif CURRENT_LEVEL == 2 and remaining_mid_patients:
        CURRENT_PATIENT = remaining_mid_patients.pop(0)
        patient_selected = True
    elif CURRENT_LEVEL == 3 and remaining_advanced_patients:
        CURRENT_PATIENT = remaining_advanced_patients.pop(0)
        patient_selected = True
    elif CURRENT_LEVEL < 3: # All patients for current difficulty exhausted, advance to next
        CURRENT_LEVEL += 1
        display_message(f"All cases for Level {CURRENT_LEVEL - 1} completed! Advancing to Level {CURRENT_LEVEL}...", 'info')
        # Recursive call to load patient from next difficulty pool
        load_new_patient()
        return
    else: # All levels completed
        end_game(True, "All cases completed!")
        return

    if patient_selected:
        display_message(f"Level {CURRENT_LEVEL}: A new patient (ID: {CURRENT_PATIENT['id']}) has arrived. Carefully analyze the symptoms.", 'info')
        display_patient_info()
        update_status_display()

        if CURRENT_PATIENT['time_bound']:
            TIME_LIMIT_SECONDS = CURRENT_PATIENT['time_limit_seconds']
            START_TIME = time.time()
            display_message(f"🚨 This is a TIME-BOUND emergency! You have {TIME_LIMIT_SECONDS // 60} minutes and {TIME_LIMIT_SECONDS % 60} seconds to diagnose and treat! 🚨", 'warning')
            # Start timer thread for continuous visual update
            timer_stop_event.clear() # Ensure event is clear before starting new thread
            timer_thread = threading.Thread(target=_timer_update_loop)
            timer_thread.daemon = True # Allow program to exit even if thread is running
            timer_thread.start()
        else:
            # If not time-bound, ensure any previous timer is stopped
            timer_stop_event.set()

def order_test_handler(b):
    """Handles ordering a medical test."""
    global GAME_CREDITS, SCORE
    if GAME_STATE != "playing" or not CURRENT_PATIENT:
        display_message("Please start a game first.", 'error')
        return

    if check_time_limit():
        return # Time check already handled end_level

    test_name = test_dropdown.value
    if not test_name:
        display_message("Please select a test to order.", 'error')
        return

    cost = CURRENT_PATIENT['test_costs'].get(test_name, 0)
    if GAME_CREDITS < cost:
        display_message(f"Insufficient credits for {test_name}! You need ${cost}.", 'error')
        return

    GAME_CREDITS -= cost
    update_status_display()

    with game_output:
        clear_output(wait=True)
        display_message(f"🔬 Ordered {test_name}. Cost: ${cost}. Remaining Credits: ${GAME_CREDITS}", 'info')
        if test_name in CURRENT_PATIENT['test_results']:
            display(HTML(f"""
            <div style="border: 1px solid #d4edda; padding: 15px; margin-top: 15px; border-radius: 12px; background-color: #e6faed; font-family: 'Inter', sans-serif; color: #155724; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <p style="font-weight: bold; font-size: 1.1em;">{test_name} Results:</p>
                <p style="font-size: 1em; line-height: 1.4;">{CURRENT_PATIENT['test_results'][test_name]}</p>
            </div>
            """))
        else:
            display_message(f"⚠️ No specific result found for {test_name} for this patient. This test might be unnecessary for this case, incurring a penalty if diagnosis/treatment is wrong later.", 'warning')
            # For simplicity, we apply a direct penalty for potentially unnecessary tests at the time of diagnosis/treatment review.
            # No immediate credit penalty beyond the test cost itself to encourage exploration.
            # The over-testing penalty is implicitly handled if the player fails the case due to credit loss or wrong diagnosis/treatment.

def use_hint_handler(b):
    """Provides a hint to the player."""
    global HINTS_AVAILABLE, GAME_CREDITS
    if GAME_STATE != "playing" or not CURRENT_PATIENT:
        display_message("Please start a game first.", 'error')
        return

    if HINTS_AVAILABLE > 0:
        HINTS_AVAILABLE -= 1
        hint_button.description = f"Use Hint ({HINTS_AVAILABLE} left)"
        display_message(f"💡 AI Assistant Hint: {CURRENT_PATIENT['hint']}", 'info')
        GAME_CREDITS -= 50 # Hint costs credits
        update_status_display()
    else:
        display_message("🚫 No hints remaining! You're on your own now.", 'error')
    if HINTS_AVAILABLE == 0:
        hint_button.disabled = True


def make_diagnosis_handler(b):
    """Handles the diagnosis submission."""
    global SCORE, GAME_CREDITS
    if GAME_STATE != "playing" or not CURRENT_PATIENT:
        display_message("Please start a game first.", 'error')
        return

    if check_time_limit():
        return # Time check already handled end_level

    submitted_diagnosis = diagnosis_input.value.strip()
    if not submitted_diagnosis:
        display_message("Please enter a diagnosis.", 'error')
        return

    # Basic string matching for simplicity. For a real game, fuzzy matching or keyword recognition would be needed.
    if submitted_diagnosis.lower() == CURRENT_PATIENT['correct_diagnosis'].lower():
        SCORE += 100
        GAME_CREDITS += 200 # Bonus for correct diagnosis
        display_message(f"✅ Correct Diagnosis! You earned 100 points and ${200} bonus. Now administer the correct treatment.", 'success')
        update_status_display()
        # Enable treatment phase
        diagnose_button.disabled = True
        diagnosis_input.disabled = True
        treatment_input.disabled = False
        treat_button.disabled = False
        test_dropdown.disabled = True # Disable further tests once diagnosis is made
        order_test_button.disabled = True
    else:
        GAME_CREDITS -= 100 # Penalty for wrong diagnosis
        display_message(f"❌ Incorrect Diagnosis. You lost 100 credits. Remaining Credits: ${GAME_CREDITS}. Please re-evaluate and try again!", 'warning')
        update_status_display()
        if GAME_CREDITS <= 0:
            end_level(False, "Ran out of credits after incorrect diagnosis!")


def administer_treatment_handler(b):
    """Handles the treatment submission."""
    global SCORE, GAME_CREDITS
    if GAME_STATE != "playing" or not CURRENT_PATIENT:
        display_message("Please start a game first.", 'error')
        return

    if check_time_limit():
        return # Time check already handled end_level

    submitted_treatment = treatment_input.value.strip()
    if not submitted_treatment:
        display_message("Please enter a treatment.", 'error')
        return

    # Basic string matching for simplicity.
    if submitted_treatment.lower() == CURRENT_PATIENT['correct_treatment'].lower():
        SCORE += 150 # More points for correct treatment
        GAME_CREDITS += 300 # Bonus for correct treatment
        display_message(f"🎉 Correct Treatment! You earned 150 points and ${300} bonus. Patient successfully treated! Well done, Doctor!", 'success')
        end_level(True, "Successfully treated!")
    else:
        GAME_CREDITS -= 150 # Larger penalty for wrong treatment
        display_message(f"⚠️ Incorrect Treatment. You lost 150 credits. Remaining Credits: ${GAME_CREDITS}. Re-evaluate your treatment plan!", 'warning')
        update_status_display()
        if GAME_CREDITS <= 0:
            end_level(False, "Ran out of credits after incorrect treatment!")

def end_level(success, reason):
    """Ends the current level and prepares for the next or game over."""
    global CURRENT_LEVEL, GAME_STATE, GAME_CREDITS, SCORE
    global timer_thread, timer_stop_event

    # Stop the timer thread if it's running
    timer_stop_event.set()
    if timer_thread and timer_thread.is_alive():
        timer_thread.join(timeout=1) # Give it a moment to stop


    # Disable all interactive elements
    test_dropdown.disabled = True
    diagnosis_input.disabled = True
    treatment_input.disabled = True
    diagnose_button.disabled = True
    treat_button.disabled = True
    hint_button.disabled = True
    order_test_button.disabled = True


    if success:
        display_message(f"Level Complete! {reason} Your current score: {SCORE}, Credits: ${GAME_CREDITS}.", 'success')
        # Check if there are more patients for the current difficulty level
        if (CURRENT_LEVEL == 1 and remaining_basic_patients) or \
           (CURRENT_LEVEL == 2 and remaining_mid_patients) or \
           (CURRENT_LEVEL == 3 and remaining_advanced_patients):
            start_button.description = "Next Patient"
            GAME_STATE = "level_complete" # Indicates ready for next patient in current level
        elif CURRENT_LEVEL < 3: # All patients of current difficulty done, advance to next level
            start_button.description = f"Advance to Level {CURRENT_LEVEL + 1}"
            GAME_STATE = "level_complete" # Indicates ready to advance level
        else: # All levels completed
            end_game(True, "All cases completed!")
            return # Exit to prevent enabling start_button prematurely if end_game already handles it.
    else: # Failure
        display_message(f"Game Over! {reason} Your final score: {SCORE}. Better luck next time!", 'error')
        end_game(False, reason)
        return

    start_button.disabled = False # Enable start button for next action (next patient/level/new game)


def end_game(is_win, reason="Game Over"):
    """Finalizes the game session."""
    global GAME_STATE
    GAME_STATE = "game_over"

    # Ensure all controls are disabled at game end
    test_dropdown.disabled = True
    diagnosis_input.disabled = True
    treatment_input.disabled = True
    diagnose_button.disabled = True
    treat_button.disabled = True
    hint_button.disabled = True
    order_test_button.disabled = True

    if is_win:
        display_message(f"🏆 Congratulations! You've mastered Diagnostica! Final Score: {SCORE}. {reason}", 'success')
    else:
        display_message(f"💔 Game Over! Final Score: {SCORE}. Reason: {reason}", 'error')

    start_button.description = "Start New Game"
    start_button.disabled = False # Always re-enable start button to allow new game


def next_action_handler(b):
    """Handles the action when the start_button is clicked (next patient, next level, or new game)."""
    global GAME_STATE
    if GAME_STATE == "level_complete":
        # Determine if we're advancing patient within same level or moving to next difficulty
        if (CURRENT_LEVEL == 1 and remaining_basic_patients) or \
           (CURRENT_LEVEL == 2 and remaining_mid_patients) or \
           (CURRENT_LEVEL == 3 and remaining_advanced_patients):
            # Still patients left in current difficulty
            GAME_STATE = "playing"
            load_new_patient()
        elif CURRENT_LEVEL < 3:
            # No patients left in current difficulty, advance to next level
            GAME_STATE = "playing"
            load_new_patient() # load_new_patient will handle CURRENT_LEVEL increment
        else:
            # All levels/patients are exhausted
            end_game(True, "All cases completed!")
    else: # Initial start or game over, just start a fresh game.
        start_game()

# --- Widget Event Linking ---
start_button.on_click(next_action_handler) # All start/continue logic goes through this handler
hint_button.on_click(use_hint_handler)
diagnose_button.on_click(make_diagnosis_handler)
treat_button.on_click(administer_treatment_handler)
order_test_button.on_click(order_test_handler)


# --- Initial GUI Setup ---
def setup_gui():
    """Sets up the initial GUI layout."""
    global game_container

    # Arrange buttons and inputs for actions
    action_controls = widgets.VBox([
        widgets.HBox([test_dropdown, order_test_button], layout=widgets.Layout(justify_content='space-between')),
        diagnosis_input,
        diagnose_button,
        treatment_input,
        treat_button,
        hint_button
    ], layout=widgets.Layout(border='1px solid #ddd', padding='20px', border_radius='15px', background_color='#f0f8ff', box_shadow='2px 2px 10px rgba(0,0,0,0.08)'))

    # Main layout
    game_container = widgets.VBox([
        widgets.HTML("""
            <h1 style='color: #2c3e50; text-align: center; font-family: "Inter", sans-serif; font-size: 2.5em; margin-bottom: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);'>
                <span style='color: #3498db;'>🩺 Diagnostica:</span> Virtual Medical Case Simulator 🔬
            </h1>
        """),
        widgets.HBox([start_button], layout=widgets.Layout(justify_content='center', margin='10px 0 20px 0')),
        status_output,
        patient_info_output,
        game_output,
        widgets.HTML("<hr style='border-top: 2px dashed #ccc; margin: 30px 0;'>"), # Separator
        widgets.HTML("<h2 style='color: #2c3e50; text-align: center; font-family: \"Inter\", sans-serif; font-size: 1.8em; margin-bottom: 20px;'>Your Actions:</h2>"),
        action_controls
    ], layout=widgets.Layout(border='2px solid #a0a0a0', padding='25px', border_radius='20px', background_color='#ffffff', box_shadow='5px 5px 15px rgba(0,0,0,0.2)', max_width='800px', margin='auto'))

    display(game_container)
    update_status_display()
    display_message("Click 'Start New Game' to begin your biomedical internship!", 'info')

# Call setup_gui to display the game interface when the notebook runs
setup_gui()

