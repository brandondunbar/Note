#!/usr/bin/env python3
"""A note keeping app, sorting notes by directory.

Usage:

    python3 Note/main.py

"""

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import WidgetException

import configparser
import os

# My scripts:
import note_manager
from note_class import Note

config = configparser.ConfigParser()


# App-wide variables:
class Settings:
    """Settings for the app. Allows user defined colors, which change when app
    is reopened."""

    def __init__(self):
        """Loads color preferences and store them for accessibility."""

        # Load settings
        self.settings = self.load_settings()

        colors = self.settings["Colors"]

        # Assign colors to attributes
        self.text_color = [float(color) for color in colors["Text Color"][1:-1].split(",")]
        self.app_bg_color = [float(color) for color in colors["App Bg Color"][1:-1].split(",")]
        self.textinput_color = [float(color) for color in colors["TextInput Color"][1:-1].split(",")]

        self.window_color = self.app_bg_color

    def save_settings(self, settings):
        """Saves user settings when Settings screen is exited.

        Args:
            settings: The config file."""

        with open('settings.ini', 'w') as config_file:
            settings.write(config_file)

    def load_settings(self):
        """Loads user settings from config file.
        Failing that, creates one.

        Returns:
            settings: The config file"""

        # Create a settings file if there isn't one
        if not os.path.isfile('settings.ini'):
            self.initialize_config()

        # Store it
        config.read('settings.ini')
        settings = config

        return settings

    def initialize_config(self):
        """Initializes the user settings.ini

        Returns:
            config: The settings config file."""

        # Config file set up
        config['Colors'] = {'Text Color': [0, 1, 1, 1],
                            'App Bg Color': [0, 0, 0, 1],
                            'TextInput Color': [.25, .25, .25, 1]}
        # Save config file
        self.save_settings(config)


class AppVariables:
    """Non-global global variables."""

    default_colors = [[0, 1, 1, 1], [0, 0, 0, 1], [.25, .25, .25, 1]]
    notes = note_manager.load()
    active_notebook = None
    active_note = None


# Redefined widgets:
class LabelButton(ButtonBehavior, Label):
    """A Kivy Widget for displaying text, modified for button behavior"""

    def on_press(self):
        sm.current = 'menu'


class TopBar(BoxLayout):
    """The bar on the top of each screen.

    Args:
        button1: The left button
        button2: The right button

    If one or both are not passed, a placeholder button is created to
    preserve placement of the 'Note' label."""

    def __init__(self, button1=None, button2=None, **kwargs):
        super(TopBar, self).__init__(**kwargs)

        self.size_hint_y = .1
        buttons = []

        if button1:
            buttons.append(button1)
        else:
            blank_button = Button(background_normal='',
                                  background_down='',
                                  background_color=app_settings.app_bg_color,
                                  size_hint=(.15, 1))
            buttons.append(blank_button)

        if button2:
            buttons.append(button2)
        else:
            blank_button = Button(background_normal='',
                                  background_down='',
                                  background_color=app_settings.app_bg_color,
                                  size_hint=(.15, 1))
            buttons.append(blank_button)

        for button in buttons:

            button.background_normal = ''
            button.background_color = app_settings.app_bg_color
            button.color = app_settings.text_color
            button.size_hint = (.15, 1)

        title = LabelButton(text="Note",
                            font_size=25,
                            color=app_settings.text_color)

        self.add_widget(buttons[0])
        self.add_widget(title)
        self.add_widget(buttons[1])


class CustomTextInput(TextInput):
    """A Label widget with a background color."""

    def __init__(self, **kwargs):
        super(CustomTextInput, self).__init__(**kwargs)

        self.foreground_color = app_settings.text_color  # Font color

        self.background_active = ''  # Background styling/coloring
        self.background_normal = ''
        self.background_color = app_settings.textinput_color


# Screens:
class MenuScreen(Screen):
    """The uppermost screen in an hierarchical view, shows on load."""

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        # Screen Container
        screen_container = BoxLayout(orientation="vertical",
                                     spacing=5)

        # *Top Bar-------------------------------------------------------------

        #       New Button
        note_btn = Button(text="+",
                          id="New")
        note_btn.bind(on_release=self.switch_screen)

        #       Settings Button
        settings_btn = Button(text="*",
                              id='Settings')
        settings_btn.bind(on_release=self.switch_screen)

        top_bar = TopBar(button1=note_btn,
                         button2=settings_btn)
        screen_container.add_widget(top_bar)

        # *Screen Content------------------------------------------------------

        #       Populate Notebooks layout
        self.notebooks = BoxLayout(orientation='vertical',
                                   spacing=2)
        self.notebooks.bind(minimum_height=self.notebooks.setter('height'))

        #       Make scrollable
        self.nb_scroll = ScrollView(size_hint=(1, 1),
                                    size=(1, 1),
                                    bar_color=app_settings.text_color,
                                    bar_pos_y='right')
        self.nb_scroll.add_widget(self.notebooks)
        screen_container.add_widget(self.nb_scroll)

        # Pack
        self.add_widget(screen_container)

        # Load notebooks
        self.bind(on_enter=self.load)

    def switch_screen(self, *args):
        """A method for switching screens.

        Args:
            args[0]: The button object selected, passed automatically."""

        if args[0].id == 'New':
            AppVariables.active_notebook = None
            sm.current = 'newnotebook'

        elif args[0].id == 'Settings':
            sm.current = 'settings'

        else:
            AppVariables.active_notebook = args[0].id
            sm.current = 'notebook'

    def load(self, *args):
        """Loads all notebooks when screen loads."""

        AppVariables.active_notebook = None
        AppVariables.active_note = None
        self.notebooks.clear_widgets()

        if len(AppVariables.notes.items()) > 0:
            for notebook_name, notebook in AppVariables.notes.items():
                notebook_btn = Button(text=notebook_name,
                                      size_hint=(1, None),
                                      background_normal='',
                                      background_color=app_settings.textinput_color,
                                      color=app_settings.text_color,
                                      id=notebook_name)
                self.notebooks.add_widget(notebook_btn)
                notebook_btn.bind(on_press=lambda button:
                                  self.switch_screen(button))

            #       Buffer
            self.notebooks.add_widget(Label(text="",
                                            size_hint=(0, 1-(len(
                                            AppVariables.notes.keys())*.1))))

        else:
            self.notebooks.add_widget(Label(text="No Notebooks to display :("))


class NewNotebookScreen(Screen):
    """The screen for creating a new notebook. Simply asks for a name."""

    def __init__(self, **kwargs):
        super(NewNotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        screen_container = BoxLayout(orientation="vertical",
                                     padding=[1])

        # *Top Bar-------------------------------------------------------------
        screen_container.add_widget(TopBar())

        #       Buffer
        content_container = BoxLayout(orientation='vertical')
        content_container.add_widget(Label(text="",
                                           size_hint=(1, .5)))

        # *Notebook Name Entry-------------------------------------------------
        self.nb_name = CustomTextInput(hint_text="Notebook Name...",
                                       multiline=False,
                                       size_hint=(1, .085),)
        self.nb_name.bind(on_text_validate=self.save)
        content_container.add_widget(self.nb_name)

        #       Buffer
        content_container.add_widget(Label(text="",
                                           size_hint=(1, .5)))

        # *Save Button---------------------------------------------------------
        save_btn = Button(text='Save',
                          size_hint=(1, .2),
                          color=app_settings.text_color,
                          background_color=app_settings.textinput_color,)
        save_btn.bind(on_release=self.save)
        content_container.add_widget(save_btn)

        # Pack
        screen_container.add_widget(content_container)
        self.add_widget(screen_container)

    def switch_screen(self, *args):
        """A method for switching screens."""
        sm.current = 'notebook'

    def save(self, *args):
        """Method to properly save the new notebook."""
        name = self.nb_name.text

        if name:
            AppVariables.notes[name] = []
            AppVariables.active_notebook = name
            self.nb_name.text = ''
            note_manager.save(AppVariables.notes)
            sm.current = 'notebook'


class NotebookScreen(Screen):
    """The screen for viewing the notes inside a notebook, each note
    represented by a button that leads to the View Note screen. Can also add
    a note or delete the entire notebook from the top bar."""

    def __init__(self, **kwargs):
        super(NotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.notebook_container = BoxLayout(orientation="vertical",
                                            padding=[1])

        # *Top Bar-------------------------------------------------------------
        #       New Button
        new_btn = Button(text="+",
                         id="New")
        new_btn.bind(on_release=self.switch_screen)

        #       Settings Button
        delete_btn = Button(text="|||")
        delete_btn.bind(on_release=self.delete)
        #       Pack
        self.notebook_container.add_widget(TopBar(new_btn, delete_btn))

        # *Active Notebook Label-----------------------------------------------
        active_nb = ''
        if AppVariables.active_notebook is not None:
            active_nb = AppVariables.active_notebook

        self.current_notebook = Label(text=active_nb,
                                      color=app_settings.textinput_color,
                                      size_hint=(1, .1))
        self.notebook_container.add_widget(self.current_notebook)
        self.no_note_lbl = Label(text="No notes to display")

        # *Note Container------------------------------------------------------
        self.notes = BoxLayout(orientation="vertical",
                               spacing=1)
        self.notebook_container.add_widget(self.notes)

        # Pack
        self.add_widget(self.notebook_container)
        # Update widgets on screen entry
        self.bind(on_enter=self.update_widgets)

    def switch_screen(self, *args):
        """A method for switching screens.

        Args:
            args[0]: The button object selected, passed
            automatically.
            args[1]: A Note object. Not passed if it's a new note."""

        try:
            AppVariables.active_note = args[1]

        except IndexError:
            pass

        sm.current = 'editnote'

    def update_widgets(self, *args):
        """Updates the Notebook container"""

        def new_note_btn(note):
            """Populates the notebook container with buttons representing
            notes.

            Args:
                note: The note object to represent."""

            note_btn = Button(text=note.name,
                              size_hint=(1, None),
                              background_normal='',
                              background_color=app_settings.textinput_color,
                              color=app_settings.text_color)

            note_btn.bind(on_press=lambda button:
                          self.switch_screen(button, note))

            return note_btn

        self.current_notebook.text = AppVariables.active_notebook
        self.current_notebook.color = app_settings.textinput_color

        if len(AppVariables.notes[AppVariables.active_notebook]) > 0:
            self.notes.clear_widgets()

            for note in AppVariables.notes[AppVariables.active_notebook]:
                note_btn = new_note_btn(note)
                self.notes.add_widget(note_btn)

            self.notes.add_widget(Label(text=""))

        else:  # If there are no notes to display
            try:
                self.notes.clear_widgets()
                self.notes.add_widget(self.no_note_lbl)  # Say so

            except WidgetException:
                pass  # WidgetException raised if navigating back to the screen

    def delete(self, *args):
        """Method for deleting a notebook"""
        notebook_lbl = self.current_notebook
        if "Delete" not in notebook_lbl.text:
            notebook_lbl.text = f"Delete {AppVariables.active_notebook}?"
            notebook_lbl.color = [1, 0, 0, 1]
        else:
            del AppVariables.notes[AppVariables.active_notebook]
            note_manager.save(AppVariables.notes)
            sm.current = 'menu'


class EditNoteScreen(Screen):
    """Screen for editing a note's name and content. When a new note is to be
    created the user is redirected here to create it."""

    def __init__(self, **kwargs):
        super(EditNoteScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.note_container = BoxLayout(orientation="vertical",
                                        spacing=5)

        # *Top Bar-------------------------------------------------------------

        #       Back Button
        back_btn = Button(text="<-",
                          background_normal='',
                          background_color=app_settings.app_bg_color,
                          color=app_settings.text_color,
                          size_hint=(.15, 1),
                          id="Back")
        back_btn.bind(on_release=self.back)

        #       Settings Button
        delete_btn = Button(text="|||",
                            background_normal='',
                            background_color=app_settings.app_bg_color,
                            color=app_settings.text_color,
                            size_hint=(.15, 1))
        delete_btn.bind(on_release=self.delete)

        self.note_container.add_widget(TopBar(back_btn, delete_btn))

        # *Current Notebook Label----------------------------------------------
        active_nb = ''
        if AppVariables.active_notebook is not None:
            active_nb = AppVariables.active_notebook

        self.current_notebook = Label(text=active_nb,
                                      color=app_settings.textinput_color,
                                      size_hint=(1, .1))
        self.note_container.add_widget(self.current_notebook)

        # *Note Name-----------------------------------------------------------
        name_container = BoxLayout(size_hint_y=.1)

        #       Buffer
        name_container.add_widget(Label(size_hint_x=.025))

        #       Name Text Input
        self.note_name_ti = CustomTextInput(hint_text="Untitled",
                                            font_size=18,
                                            multiline=False,
                                            write_tab=False,
                                            size_hint=(1, 1),
                                            padding=(10, 10))
        name_container.add_widget(self.note_name_ti)

        #       Buffer
        name_container.add_widget(Label())

        self.note_container.add_widget(name_container)
        self._name = 'Untitled'  # This is the default title for notes

        # *Note Body-----------------------------------------------------------
        body_container = BoxLayout()

        #       Buffer
        body_container.add_widget(LabelButton(size_hint_x=.01))

        #       The ScrollView

        self.body_scroll = ScrollView(size_hint=(1, 1),
                                      size=(1, 1),
                                      bar_color=app_settings.text_color,
                                      bar_pos_y='right', )

        #       Body TextInput Widget
        self.notebody_textinput = CustomTextInput(hint_text="Enter note body...",
                                                  multiline=True,
                                                  size_hint_y=None,
                                                  padding=(10, 10))

        # Bind the two widgets to the greater height
        self.body_scroll.bind(height=self.textinput_height)
        self.notebody_textinput.bind(minimum_height=self.textinput_height)

        self.body_scroll.add_widget(self.notebody_textinput)

        body_container.add_widget(self.body_scroll)

        #       Buffer
        body_container.add_widget(LabelButton(size_hint_x=.01))

        self.note_container.add_widget(body_container)

        #       Buffer
        self.note_container.add_widget(Label(size_hint_y=.005))

        # *Pack----------------------------------------------------------------
        self.add_widget(self.note_container)

        # *Edit or New?--------------------------------------------------------
        self.bind(on_enter=self.load)

    def back(self, *args):
        """Method for back button, saves the note."""

        self.save()

        sm.current = 'notebook'

    def save(self, *args):
        """Save the note."""

        if self.notebody_textinput.text.strip() != '':
            # Assign notebook list to variable for readability
            notebook = AppVariables.notes[AppVariables.active_notebook]

            if self.note_name_ti.text != '':
                self._name = self.note_name_ti.text

            if AppVariables.active_note is None:  # If we're adding a new note
                note = Note(name=self._name,
                            body=self.notebody_textinput.text.strip())  # Create a new Note object
                notebook.append(note)  # Add it to the notebook
                AppVariables.active_note = note  # Set it as active

            else:  # If we're editing an existing
                # Find note and overwrite it
                for index, item in enumerate(notebook):
                    if item.name.strip() == AppVariables.active_note.name:
                        notebook[index].name = self.note_name_ti.text
                        notebook[index].body = self.notebody_textinput.text.strip()

            self.note_name_ti.text = ''
            self.notebody_textinput.text = ''

            note_manager.save(AppVariables.notes)

    def load(self, *args):
        """
        Loads data and populates TextInput widgets.

        I had to take away the y hint to use the ScrollView Widget, which led
        to a crappy resizing while typing behavior. Working on a better
        solution.
        """

        self.current_notebook.text = AppVariables.active_notebook
        self.current_notebook.color = app_settings.textinput_color

        if AppVariables.active_note is not None:
            self.note_name_ti.text = AppVariables.active_note.name
            self.notebody_textinput.text = AppVariables.active_note.body

        else:
            self.note_name_ti.text = ''  # New note
            self.notebody_textinput.text = ''

    def delete(self, *args):
        """Deletes Note. If it's a new note, should we clear the TextInput
        widgets?"""
        if AppVariables.active_note is not None:  # If this isn't a new note
            if "Delete" not in self.current_notebook.text:
                self.current_notebook.text = \
                    f"Delete {AppVariables.active_note}?"
                self.current_notebook.color = [1, 0, 0, 1]
            else:
                notes = AppVariables.notes[AppVariables.active_notebook]
                for index, note in enumerate(notes):
                    if notes[index] == AppVariables.active_note:
                        del notes[index]
                        note_manager.save(AppVariables.notes)
                AppVariables.active_note = None
                sm.current = 'notebook'

    def textinput_height(self, *args):
        self.notebody_textinput.height = max(self.notebody_textinput.minimum_height, self.body_scroll.height)


class SettingsScreen(Screen):
    """A screen for editing the App Settings."""

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        screen_cntnr = BoxLayout(orientation='vertical',
                                 spacing=5)
        contents_cntnr = BoxLayout(orientation='vertical',
                                   spacing=5)
        self.settings_cntnr = GridLayout(cols=2,
                                         spacing=1)

        # *Top Bar-------------------------------------------------------------

        #       Back Button
        back_btn = Button(text="<-",
                          background_normal='',
                          background_color=app_settings.app_bg_color,
                          color=app_settings.text_color,
                          size_hint=(.15, 1),
                          id="Back")
        back_btn.bind(on_release=self.back)

        screen_cntnr.add_widget(TopBar(back_btn))

        # *Message Label-------------------------------------------------------
        self.msg_lbl = Label(text='Changes will take effect when program'
                                  ' opens next.',
                             size_hint=(1, .1))
        contents_cntnr.add_widget(self.msg_lbl)

        # *Colors--------------------------------------------------------------
        #       Text Color
        primary_label = Label(text='Text Color: ',
                              color=app_settings.text_color,
                              size_hint=(1, .05))
        self.primary_ti = CustomTextInput(text=str(app_settings.text_color),
                                          multiline=False,
                                          size_hint=(1, .05))
        #       Bind
        self.settings_cntnr.add_widget(primary_label)
        self.settings_cntnr.add_widget(self.primary_ti)

        #       Secondary
        secondary_label = Label(text='App Background Color: ',
                                color=app_settings.text_color,
                                size_hint=(1, .05))
        self.secondary_ti = CustomTextInput(text=str(app_settings.app_bg_color),
                                            multiline=False,
                                            size_hint=(1, .05))
        #       Bind
        self.settings_cntnr.add_widget(secondary_label)
        self.settings_cntnr.add_widget(self.secondary_ti)

        #       Tertiary
        tertiary_label = Label(text='Tertiary Color: ',
                               color=app_settings.text_color,
                               size_hint=(1, .05))
        self.tertiary_ti = CustomTextInput(text=str(app_settings.textinput_color),
                                           multiline=False,
                                           size_hint=(1, .05))
        #       Bind
        self.settings_cntnr.add_widget(tertiary_label)
        self.settings_cntnr.add_widget(self.tertiary_ti)

        # *Default Button----------------------------------------------------
        self.default_button = Button(text="Reset to Default",
                                     background_normal='',
                                     background_color=app_settings.app_bg_color,
                                     color=app_settings.text_color,
                                     size_hint=(1, .5))
        self.default_button.bind(on_release=self.set_default)

        contents_cntnr.add_widget(self.settings_cntnr)
        contents_cntnr.add_widget(self.default_button)

        screen_cntnr.add_widget(contents_cntnr)
        self.add_widget(screen_cntnr)

    def back(self, *args):
        """Method for leaving the screen, saves on exit."""

        self.save()
        sm.current = 'menu'

    def set_default(self, *args):
        """Reverts color fields to default."""

        primary_default = AppVariables.default_colors[0]
        secondary_default = AppVariables.default_colors[1]
        tertiary_default = AppVariables.default_colors[2]

        self.primary_ti.text = str(primary_default)
        self.secondary_ti.text = str(secondary_default)
        self.tertiary_ti.text = str(tertiary_default)
        self.save()

    def save(self):
        """Saves values from input boxes to settings."""

        def parse_color(color):
            """Converts string to list to be stored.

            Args:
                color: The string (r, g, b, s) to be converted

            Returns:
                A usable list representing a color, to be used by Kivy."""

            color_list = color
            return color_list

        settings = []

        try:
            text_color = parse_color(self.primary_ti.text)
        except ValueError:
            text_color = app_settings.text_color
        try:
            app_bg_color = parse_color(self.secondary_ti.text)
        except ValueError:
            app_bg_color = app_settings.app_bg_color
        try:
            textinput_color = parse_color(self.tertiary_ti.text)
        except ValueError:
            textinput_color = app_settings.textinput_color

        config['Colors'] = {'Text Color': text_color,
                            'App Bg Color': app_bg_color,
                            'TextInput Color': textinput_color}

        app_settings.save_settings(config)


# Instantiate settings for them to take effect
app_settings = Settings()

# Screen Manager object manages which screen is visible
sm = ScreenManager(transition=NoTransition())
screens = [MenuScreen(name='menu'),
           NotebookScreen(name='notebook'),
           NewNotebookScreen(name='newnotebook'),
           EditNoteScreen(name="editnote"),
           SettingsScreen(name="settings")]

for screen in screens:
    sm.add_widget(screen)


class NoteApp(App):
    """Represents the application itself, Window settings modified here."""

    def build(self):
        # I don't want a white window background
        Window.clearcolor = app_settings.window_color
        Window.size = (500, 550)  # Set window size
        return sm  # Return screen manager, runs app


if __name__ == '__main__':
    NoteApp().run()
