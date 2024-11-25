# -*- coding: utf-8 -*-
from psychopy import event, core, data, gui, visual
from fileHandling import *


class Experiment:
    def __init__(self, win_color, txt_color):
        self.stimuli_positions = [[-.2, 0], [.2, 0], [0, 0]]
        self.win_color = win_color
        self.txt_color = txt_color

    def create_window(self, color=(1, 1, 1)):
        color = self.win_color
        win = visual.Window(monitor="testMonitor",
                            color=color, fullscr=True)
        return win

    def settings(self):
        experiment_info = {'Subid': '', 'Age': '', 'Experiment Version': 0.1,
                           'Sex': ['Male', 'Female', 'Other'],
                           'Language': ['English', 'Chinese'], 
                            'Total Sessions': 4,  # Total number of sessions
                            'Current Session': 1,  # Starting session
                            u'date': data.getDateStr(format="%Y-%m-%d_%H:%M")}

        info_dialog = gui.DlgFromDict(title='Stroop task', dictionary=experiment_info,
                                      fixed=['Experiment Version'])
        experiment_info[u'DataFile'] = u'Data' + os.path.sep + u'stroop.csv'

        if info_dialog.OK:
            return experiment_info
        else:
            core.quit()
            return 'Cancelled'

    def manage_sessions(self, settings):
        session_order = [
            {'language': 'English', 'trial_file': 'practice_list.csv', 'type': 'practice', 'display_name': 'Session 1 English Practice'},
            {'language': 'English', 'trial_file': 'practice_list.csv', 'type': 'test', 'display_name': 'Session 2 English Test'},
            {'language': 'Chinese', 'trial_file': 'practice_list.csv', 'type': 'practice', 'display_name': 'Session 3 Chinese Practice'},
            {'language': 'Chinese', 'trial_file': 'practice_list.csv', 'type': 'test', 'display_name': 'Session 4 Chinese Test'}
        ]
        
        current_session = settings['Current Session'] - 1
        
        if current_session < len(session_order):
            current_config = session_order[current_session]
            settings['Language'] = current_config['language']
            return current_config
        else:
            return None

    def create_text_stimuli(self, text=None, pos=[0.0, 0.0], name='', color=None):
        if color is None:
            color = self.txt_color
        text_stimuli = visual.TextStim(win=window, ori=0, name=name,
                                       text=text, font=u'Songti SC',
                                       pos=pos,
                                       color=color, 
                                       colorSpace=u'rgb', 
                                       height=0.03, 
                                       wrapWidth=2)
        return text_stimuli

    def create_trials(self, trial_file, randomization='random'):
        data_types = ['Response', 'Accuracy', 'RT', 'Sub_id', 'Sex']
        with open(trial_file, 'r') as stimfile:
            _stims = csv.DictReader(stimfile)
            trials = data.TrialHandler(list(_stims), 1,
                                       method="random")
        [trials.data.addDataType(data_type) for data_type in data_types]

        return trials

    def present_stimuli(self, color, text, position, stim):
        _stimulus = stim
        position = position
        if settings['Language'] == "Chinese":
            text = swedish_task(text)
        else:
            text = text
        _stimulus.pos = position
        _stimulus.setColor(color)
        _stimulus.setText(text)
        return _stimulus

    def running_experiment(self, trials, testtype):
        _trials = trials
        testtype = testtype
        timer = core.Clock()
        stimuli = [self.create_text_stimuli() for _ in range(4)]

        for trial in _trials:
            # Fixation cross
            fixation = self.present_stimuli(self.txt_color, '+', self.stimuli_positions[2],
                                            stimuli[3])
            fixation.draw()
            window.flip()
            core.wait(.6)
            timer.reset()

            # Target word
            target = self.present_stimuli(trial['colour'], trial['stimulus'],
                                          self.stimuli_positions[2], stimuli[0])
            target.draw()
            # alt1
            alt1 = self.present_stimuli(self.txt_color, trial['alt1'],
                                        self.stimuli_positions[0], stimuli[1])
            alt1.draw()
            # alt2
            alt2 = self.present_stimuli(self.txt_color, trial['alt2'],
                                        self.stimuli_positions[1], stimuli[2])
            alt2.draw()
            window.flip()

            keys = event.waitKeys(keyList=['x', 'm', 'q'])
            resp_time = timer.getTime()
            if testtype == 'practice':
                if keys[0] != trial['correctresponse']:
                    instruction_stimuli['incorrect'].draw()
                else:
                    instruction_stimuli['right'].draw()
                window.flip()
                core.wait(2)

            if testtype == 'test':
                if keys[0] == trial['correctresponse']:
                    trial['Accuracy'] = 1
                else:
                    trial['Accuracy'] = 0

                trial['RT'] = resp_time
                trial['Response'] = keys[0]
                trial['Sub_id'] = settings['Subid']
                trial['Sex'] = settings['Sex']
                write_csv(settings[u'DataFile'], trial)

            event.clearEvents()
            if 'q' in keys:
                return False

        # 显示session完成信息
        rest_text = f"\n\n{session_config['display_name']} completed.\nPress SPACE to continue."
        rest_stim = visual.TextStim(window, text=rest_text, height=0.06, color=self.txt_color)
        rest_stim.draw()
        window.flip()
        event.waitKeys(keyList=['space'])
        event.clearEvents()
        settings['Current Session'] += 1  # 在session完成后增加session计数
                
        return True


def create_instructions_dict(instr):
    start_n_end = [w for w in instr.split() if w.endswith('START') or w.endswith('END')]
    keys = {}

    for word in start_n_end:
        key = re.split("[END, START]", word)[0]

        if key not in keys.keys():
            keys[key] = []

        if word.startswith(key):
            keys[key].append(word)
    return keys


def create_instructions(input, START, END, color="Black"):
    instruction_text = parse_instructions(input, START, END)
    text_stimuli = visual.TextStim(window, text=instruction_text, wrapWidth=1.2,
                                   alignHoriz='center', color=color,
                                   alignVert='center', height=0.06)

    return text_stimuli


def display_instructions(start_instruction=''):
    if start_instruction == 'Practice':
        instruction_stimuli['instructions'].pos = (0.0, 0.5)
        instruction_stimuli['instructions'].draw()

        positions = [[-.2, 0], [.2, 0], [0, 0]]
        examples = [experiment.create_text_stimuli() for pos in positions]
        example_words = ['green', 'blue', 'green']
        if settings['Language'] == 'Chinese':
            example_words = [swedish_task(word) for word in example_words]

        for i, pos in enumerate(positions):
            examples[i].pos = pos
            if i == 0:
                examples[0].setText(example_words[i])
            elif i == 1:
                examples[1].setText(example_words[i])
            elif i == 2:
                examples[2].setColor('Green')
                examples[2].setText(example_words[i])

        [example.draw() for example in examples]

        instruction_stimuli['practice'].pos = (0.0, -0.5)
        instruction_stimuli['practice'].draw()

    elif start_instruction == 'Test':
        instruction_stimuli['test'].draw()

    elif start_instruction == 'End':
        instruction_stimuli['done'].draw()

    window.flip()
    event.waitKeys(keyList=['space'])
    event.clearEvents()


def swedish_task(word):
    swedish = '+'
    if word == "blue":
        swedish = "蓝色"
    elif word == "red":
        swedish = "红色"
    elif word == "green":
        swedish = "绿色"
    elif word == "yellow":
        swedish = "黄色"
    return swedish


if __name__ == "__main__":
    background = "Black"
    back_color = (0, 0, 0)
    textColor = "White"
    experiment = Experiment(win_color=background, txt_color=textColor)
    
    settings = experiment.settings()
    language = settings['Language']
    instructions = read_instructions_file("INSTRUCTIONS", language, language + "End")
    instructions_dict = create_instructions_dict(instructions)
    instruction_stimuli = {}

    window = experiment.create_window(color=back_color)

    for inst in instructions_dict.keys():
        instruction, START, END = inst, instructions_dict[inst][0], instructions_dict[inst][1]
        instruction_stimuli[instruction] = create_instructions(instructions, START, END, color=textColor)

    # We don't want the mouse to show:
    event.Mouse(visible=False)

    # Show initial instructions
    display_instructions(start_instruction='Practice')
    
    # Main experiment loop
    continue_experiment = True
    while continue_experiment:
        # Get next session configuration
        session_config = experiment.manage_sessions(settings)
        
        if session_config is None:
            # All sessions completed
            break
            
        # Run the session
        trials = experiment.create_trials(session_config['trial_file'])
        continue_experiment = experiment.running_experiment(
            trials, 
            session_config['type']
        )
        
        if not continue_experiment:
            break  # Exit if experiment was quit
    
    # End experiment but first we display some instructions
    display_instructions(start_instruction='End')
    window.close()