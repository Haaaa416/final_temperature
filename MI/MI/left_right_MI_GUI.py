from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet
import time
from mindcontrolrobots.utils.marker import OutletMIMarker
import tkinter as tk
import random
import os 
import sys

# Filter the non critical GL Exception that can be ignored
class GLExceptionFilter:
    def __init__(self):
        self._stderr = sys.__stderr__  # original stderr
        self._buffer = []
        self._gl_exception_detected = False

    def write(self, text):
        self._buffer.append(text)
        if "GLException" in text:
            self._gl_exception_detected = True

    def flush(self):
        if not self._gl_exception_detected:
            for line in self._buffer:
                self._stderr.write(line)
        self._buffer.clear()
        self._gl_exception_detected = False
        self._stderr.flush()

    def isatty(self):
        return self._stderr.isatty()
    
    def close(self):
        self._stderr.close()

sys.stderr = GLExceptionFilter()

def display_instruction_with_duration(win, text, duration, image=None):
    # Step 1: Show image (if any) and text
    if image:
        img_stim = visual.ImageStim(win, image=image, pos=(0, 0.3), size=(0.5, 0.5), units='norm')
        img_stim.draw()

    instruction = visual.TextStim(win, text=text, pos=(0, -0.6), color='white', height=0.07, units='norm')
    instruction.draw()
    win.flip()
    core.wait(duration)

    if image:
        del img_stim

# Function to display instructions
def display_instructions_with_wait_return(win, text):
    instruction = visual.TextStim(win, text=text, height=0.05, wrapWidth=1.5)
    instruction.draw()
    win.flip()
    event.waitKeys(keyList=["return"])  # Wait for the participant to press 'space' to proceed
    # event.waitKeys() 

def create_icon_stim(win, icon):
    # If icon is a string, determine how to render it
    if isinstance(icon, str):
        if icon == "+":
            icon = visual.TextStim(win, text='+', color='white', height=0.1, units='norm')
        elif os.path.isfile(icon) and icon.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            icon = visual.ImageStim(win, image=icon, pos=(0, 0.3), size=(0.5, 0.5), units='norm')
        else:
            # Fallback: display the raw string as text
            icon = visual.TextStim(win, text=icon, color='white', height=0.1, units='norm')
    return icon

def show_countdown(win, seconds, icon):
    icon_stim = create_icon_stim(win, icon)
    # Show countdown
    for i in range(seconds, 0, -1):
        countdown_text = visual.TextStim(win, text=f"Starting in {i} seconds", height=0.05, pos=(0, -0.5))
        icon_stim.draw()
        countdown_text.draw()
        win.flip()
        core.wait(1)

def show_fixtation(win, duration):
    # Step 2: Show fixation for 1 second
    fixation = visual.TextStim(win, text='+', color='white', height=0.1, units='norm')
    fixation.draw()
    win.flip()
    core.wait(duration)

# Function to show remaining time during the task with an icon
def show_remaining_time(win, instruction, icon, duration):
    if icon:
        icon_stim = create_icon_stim(win, icon)
    start_time = time.time()
    while time.time() - start_time < duration:
        remaining = duration - int(time.time() - start_time)
        task_text = visual.TextStim(
            win,
            text=f"{instruction}\nTime left: {remaining} seconds",
            height=0.05,
            pos=(0, -0.5),
            wrapWidth=1.5,
        )
        if icon:
            icon_stim.draw()
        task_text.draw()
        win.flip()
        core.wait(1)

# Update run_action to use the icon drawing functions
def run_action(win, action, collect_data=True, outlet = None):
    if action["label"] == "Rest":
        # Rest phase
        instruction_text = visual.TextStim(
            win,
            text=f"{action['instruction']}",
            height=0.05,
            wrapWidth=1.5,
        )
        instruction_text.draw()
        win.flip()
        core.wait(4)

        if collect_data:
            print(f"Collecting EEG data for task: {action['label']} for {action['duration']} seconds...")
            outlet.push_sample([action['start_trigger'].value])
            show_remaining_time(win, f"Rest remain for {action['duration']} seconds...", None, action['duration'])
            outlet.push_sample([action['end_trigger'].value])
            print("Data collection complete.")
        else:
            show_remaining_time(win, f"Rest and stay still for {action['duration']} seconds...", None, action['duration'])

    else:
        # Show instruction with duration
        display_instruction_with_duration(
            win,
            f"Task: {action['instruction']}\nPerform for {action['duration']} seconds.",
            2,
            image=action["icon"]
        )
        
        # Show countdown with the icon
        # show_countdown(win, 3, action['icon'])
        if collect_data:
            outlet.push_sample([OutletMIMarker.START_FIXTATION.value])
            show_fixtation(win, 2)
            outlet.push_sample([OutletMIMarker.END_FIXTATION.value])
        else:
            show_fixtation(win, 2)

        # Display task instruction with remaining time and the icon
        if collect_data:
            print(f"Collecting EEG data for task: {action['label']} for {action['duration']} seconds...")
            outlet.push_sample([action['start_trigger'].value])
            # show_remaining_time(win, action['instruction'], action['icon'], action['duration'])
            display_instruction_with_duration(win, f"Perform Motor Imagery", action["duration"])
            outlet.push_sample([action['end_trigger'].value])
            print("Data collection complete.")
        else:
            display_instruction_with_duration(win, f"Perform Motor Imagery", action["duration"])
            # show_remaining_time(win, action['instruction'], action['icon'], action['duration'])
        
        display_instruction_with_duration(win, f"Rest for 1 second", 1)

def practice_experiment(win):
    display_instruction_with_duration(win, "Practice Phase: Physically grasp the ball to internalize the kinesthetic sensation for motor imagery.", 3)

    while True:
        # === Real Grasping ===
        show_remaining_time(win, "Practice Right Hand Grasp", "./images/right_hand_grasp.png", 5)

        display_instruction_with_duration(win, "Rest 1 second", 1)

        show_remaining_time(win, "Practice Left Hand Grasp", "./images/left_hand_grasp.png", 5)

        display_instruction_with_duration(win, "Press ENTER to proceed to Next Phase, SPACE to repeat Practice Phase, or ESC to exit.", 0.1)

        while True:
            keys = event.getKeys()
            if 'escape' in keys:
                exit()
            elif 'space' in keys:
                break
            elif 'return' in keys:
                return

# Main experiment code
def motor_imagery_experiment(win, outlet):

    Actions = {
        "OpenEyeRest": {"instruction": "Rest (Open Eyes)", "label": "Rest", "icon": "+", "start_trigger": OutletMIMarker.START_OPEN_EYE_REST, "end_trigger": OutletMIMarker.END_OPEN_EYE_REST, "duration": 10},
        "CloseEyeRest": {"instruction": "Rest (Close Eyes)", "label": "Rest", "icon": "+", "start_trigger": OutletMIMarker.START_CLOSE_EYE_REST, "end_trigger": OutletMIMarker.END_CLOSE_EYE_REST, "duration": 10},
        "Left MI": {"instruction": "Imagine LEFT arm grasp", "label": "left_arm", "icon": "./images/left_hand_grasp.png", "start_trigger": OutletMIMarker.START_LEFT, "end_trigger": OutletMIMarker.END_LEFT, "duration": 10},
        "Right MI": {"instruction": "Imagine RIGHT arm grasp", "label": "right_arm", "icon": "./images/right_hand_grasp.png", "start_trigger": OutletMIMarker.START_RIGHT, "end_trigger": OutletMIMarker.END_RIGHT, "duration": 10},
    }

    try:
        # Motor Imagery Section
        motor_imagery_instructions = (
            "Motor Imagery Phase:\n"
            "Imagine the movements as instructed. Focus on the kinesthetic sensation.\n\n"
            "Press 'Enter' to begin."
        )
        display_instructions_with_wait_return(win, motor_imagery_instructions)

        # Run Rest
        run_action(win, Actions["OpenEyeRest"], collect_data=True, outlet=outlet)
        run_action(win, Actions["CloseEyeRest"], collect_data=True, outlet=outlet)

        mi_instruction = (
            "Press 'Enter' to continue to the next phase.\n"
        )
        display_instructions_with_wait_return(win, mi_instruction)

        # Action counters
        num_left_actions = 10
        num_right_actions = 10
        
        # Debug counters to verify randomness
        left_selections = 0
        right_selections = 0
        total_trials = 0

        # Main loop
        while num_left_actions > 0 or num_right_actions > 0:
            # Build candidate pool based on remaining counts
            pool = []
            if num_left_actions > 0:
                pool.append("Left MI")
            if num_right_actions > 0:
                pool.append("Right MI")

            # Sample two actions from the available ones (can be same)
            selected = random.choices(pool, k=2)
            total_trials += 1

            # Update debug counters
            for act in selected:
                if act == "Left MI":
                    left_selections += 1
                else:
                    right_selections += 1

            # Update action counters
            for act in selected:
                if act == "Left MI":
                    num_left_actions -= 1
                else:
                    num_right_actions -= 1

            print(f"Trial {total_trials}: Selected {selected}")
            print(f"Remaining actions - Left: {num_left_actions}, Right: {num_right_actions}")

            # Final action list (Rest + two sampled actions)
            action_list = [Actions[act] for act in selected]

            # Run all actions
            for action in action_list:
                run_action(win, action, collect_data=True, outlet=outlet)

            next_instruction = (
                "Press 'Enter' to continue next trial.\n"
                
            )
            display_instructions_with_wait_return(win, next_instruction)
            
        # End of experiment
        display_instructions_with_wait_return(win, "Thank you for participating!\nPress 'Enter' to exit.")
        win.close()

        # Print final statistics
        print("\nRandomization Statistics:")
        print(f"Total trials: {total_trials}")
        print(f"Left selections: {left_selections} ({left_selections/(left_selections+right_selections)*100:.1f}%)")
        print(f"Right selections: {right_selections} ({right_selections/(left_selections+right_selections)*100:.1f}%)")
    except KeyboardInterrupt:
        print("Experiment interrupted.")
        win.close()
    except Exception:
        print("Exception")
        win.close()

    core.quit()

def main(outlet):
    # Initialize PsychoPy window
    win = visual.Window(size=(800, 600), fullscr=False, color=[-1, -1, -1])
    
    # practice_experiment(win)
    motor_imagery_experiment(win, outlet)
    
def on_button_click(outlet):
    """Function to start the SSVEP experiment when the button is clicked."""
    label.config(text="Experiment started... Please focus on the screen.")
    win.update_idletasks()
    
    # Send a test marker to LabRecorder (optional)
    outlet.push_sample(["Experiment Start"])
    main(outlet)


def get_screen_size():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    return root.winfo_screenwidth(), root.winfo_screenheight()

def on_close(outlet):
    print("Closing the application and shutting down outlet...")
    outlet.__del__()  # Explicitly delete the outlet
    win.destroy()     # Close the Tk window
    sys.exit()        # Ensure full program exit

# Run the experiment
if __name__ == "__main__":
    # Send trigger to record experiment
    info = StreamInfo(name='LEFT_RIGHT_MI_Collection', type='Markers', channel_count=1, nominal_srate=0, channel_format='string', source_id='psy_marker')
    outlet = StreamOutlet(info)

     # Get screen dimensions
    [w, h] = get_screen_size()

    # Set up Tkinter GUI
    win = tk.Tk()
    win.protocol("WM_DELETE_WINDOW", lambda: on_close(outlet))
    win.title("MI Data Collection")
    win.geometry('800x600')
    
    # Instruction Label
    instruction = tk.Label(
        win,
        text=(
            "Welcome to the Motor Imagery (MI) Data Collection Interface.\n\n"
            "When you're ready, click the 'Start MI Application' button below.\n"
            "You will be guided through a series of trials where you'll be asked to imagine\n"
            "moving your left or right arm. Each trial begins with a countdown, followed by\n"
            "an instruction and an icon to help you focus on the task.\n\n"
            "Please remain still, focus on the task, and avoid unnecessary movement during\n"
            "each trial to ensure accurate EEG recordings.\n\n"
            "This program will generate event markers via the Lab Streaming Layer (LSL).\n\n"
            "▶ To record EEG and markers offline:\n"
            "  - Start your EEG acquisition software with LSL support.\n"
            "  - Open the LabRecorder and record both the EEG stream and the marker stream.\n"
            "  - The markers indicate the start and label of each task, enabling offline analysis.\n\n"
            "▶ To use the system online:\n"
            "  - Run 'online_left_right_MI_analysis.py' in parallel with this program.\n"
        ),
        font=("Arial", 12),
        fg="blue",
        justify="left",
        anchor="w"
    )
    
    instruction.pack(pady=10, padx=10)
    
    # Start Button (passes `outlet` using lambda)
    btn = tk.Button(win, text="Start MI Application", font=("Arial", 12), command=lambda: on_button_click(outlet))
    btn.pack()
    
    # Status Label (Updated when clicked)
    label = tk.Label(win, text="", font=("Arial", 10), fg="red")
    label.pack()
    
    win.mainloop()