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
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import WidgetException

import configparser
import os

# My scripts:
import note_manager

config = configparser.ConfigParser()
__version__ = 'v1.1.0'


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
        self.text_color = [float(color) for color in
                           colors["Text Color"][1:-1].split(",")]
        self.app_bg_color = [float(color) for color in
                             colors["App Bg Color"][1:-1].split(",")]
        self.textinput_color = [float(color) for color in
                                colors["TextInput Color"][1:-1].split(",")]

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

    def __init__(self):
        self.default_colors = [[0, 1, 1, 1],
                               [0, 0, 0, 1],
                               [.25, .25, .25, 1]]
        self.notes = []
        self.active_notebook = None
        self.active_note = None

    def get_note_obj(self, obj_id):
        """Searches notes for object with provided id"""

        for note_obj in self.notes:

            if note_obj[0] == obj_id:

                return note_obj


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
        self.notebooks = BoxLayout(size_hint_y=None,
                                   orientation='vertical',
                                   spacing=2)
        self.notebooks.bind(minimum_height=self.notebooks.setter('height'))

        #       Make scrollable
        self.nb_scroll = ScrollView(size_hint=(1, 1),
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
            app_variables.active_notebook = None
            sm.current = 'newnotebook'

        elif args[0].id == 'Settings':
            sm.current = 'settings'

        else:
            app_variables.active_notebook = int(args[0].id)
            sm.current = 'notebook'

    def load(self, *args):
        """Loads all notebooks when screen loads."""

        app_variables.notes = note_manager.load()
        print(app_variables.notes)

        app_variables.active_notebook = None
        app_variables.active_note = None
        self.notebooks.clear_widgets()

        child_note_objs = note_manager.get_children(0)

        if len(child_note_objs) > 0:

            for note_obj in child_note_objs:

                bg_color = app_settings.textinput_color

                notebook_btn = Button(text=note_obj[1],
                                      size_hint=(1, None),
                                      background_normal='',
                                      background_color=bg_color,
                                      color=app_settings.text_color,
                                      id=str(note_obj[0]))

                self.notebooks.add_widget(notebook_btn)

                notebook_btn.bind(on_press=lambda button:
                                  self.switch_screen(button))

            #       Buffer
            self.notebooks.add_widget(Label(text="",
                                            size_hint=(0, 1-(len(
                                                child_note_objs)*.1))))

        else:

            self.notebooks.add_widget(Label(text="No Notebooks to display :("))


class NewNotebookScreen(Screen):
    """The screen for creating a new notebook. Simply asks for a name."""

    def __init__(self, **kwargs):
        super(NewNotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        screen_container = BoxLayout(orientation="vertical",
                                     spacing=5)

        # *Top Bar-------------------------------------------------------------
        screen_container.add_widget(TopBar())

        #       Buffer
        content_container = BoxLayout(orientation='vertical')
        content_container.add_widget(Label(text="",
                                           size_hint=(1, .5)))

        # *Notebook Name Entry-------------------------------------------------
        self.nb_name = TextInput(hint_text="Notebook Name...",
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

            self.nb_name.text = ''
            note_manager.new_obj(name, "Notebook", 0)
            app_variables.notes = note_manager.load()
            app_variables.active_notebook = app_variables.notes[-1][0]

            sm.current = 'notebook'


class NotebookScreen(Screen):
    """The screen for viewing the notes inside a notebook, each note
    represented by a button that leads to the View Note screen. Can also add
    a note or delete the entire notebook from the top bar."""

    def __init__(self, **kwargs):
        super(NotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.screen_container = BoxLayout(orientation="vertical",
                                          spacing=5)

        # *Top Bar-------------------------------------------------------------
        #       New Button
        new_btn = Button(text="+",
                         id="New")
        new_btn.bind(on_release=self.switch_screen)

        #       Delete Button
        delete_btn = Button(text="|||")
        delete_btn.bind(on_release=self.delete)
        #       Pack
        self.screen_container.add_widget(TopBar(new_btn, delete_btn))

        # *Screen Content------------------------------------------------------
        self.content_container = BoxLayout(orientation="vertical",
                                           spacing=2)

        #       Active Notebook Label
        self.current_notebook = Label(color=app_settings.textinput_color,
                                      size_hint=(1, .1))
        self.content_container.add_widget(self.current_notebook)

        self.no_note_lbl = Label(text="No notes to display")

        #       Note Container
        self.notes = BoxLayout(size_hint_y=None,
                               orientation="vertical",
                               spacing=2)
        self.notes.bind(minimum_height=self.notes.setter('height'))

        #       Make scrollable
        self.note_scroll = ScrollView(size_hint=(1, 1),
                                      bar_color=app_settings.text_color,
                                      bar_pos_y='right')
        self.note_scroll.add_widget(self.notes)

        self.content_container.add_widget(self.note_scroll)
        self.screen_container.add_widget(self.content_container)

        # Pack
        self.add_widget(self.screen_container)
        # Update widgets on screen entry
        self.bind(on_enter=self.update_widgets)

    def switch_screen(self, *args):
        """A method for switching screens.

        Args:
            args[0]: The button object selected, passed
            automatically.
            args[1]: The ID of the note to edit, not passed if new note
        """

        try:
            app_variables.active_note = args[1]

        except IndexError:
            pass

        sm.current = 'editnote'

    def update_widgets(self, *args):
        """Populates the notebook container with buttons representing
            notes."""

        def new_note_btn(note):
            """Returns a button representing a note

            Args:
                note: The note object to represent."""

            note_button = Button(text=note[1],
                                 size_hint=(1, None),
                                 background_normal='',
                                 background_color=app_settings.textinput_color,
                                 color=app_settings.text_color)

            note_button.bind(on_press=lambda button:
                             self.switch_screen(button, note[0]))

            return note_button

        notebook = app_variables.get_note_obj(app_variables.active_notebook)

        self.current_notebook.text = notebook[1]
        self.current_notebook.color = app_settings.textinput_color

        notebook_children = note_manager.get_children(notebook[0])

        if len(notebook_children) > 0:

            self.notes.clear_widgets()

            for note in notebook_children:

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

            notebook_lbl.text = "Delete " + app_variables.get_note_obj(
                app_variables.active_notebook)[1] + "?"
            notebook_lbl.color = [1, 0, 0, 1]

        else:

            note_manager.delete(app_variables.active_notebook)
            app_variables.notes = note_manager.load()

            sm.current = 'menu'


class EditNoteScreen(Screen):
    """Screen for editing a note's name and content. When a new note is to be
    created the user is redirected here to create it."""

    def __init__(self, **kwargs):
        super(EditNoteScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.editnote_container = BoxLayout(orientation="vertical",
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

        self.editnote_container.add_widget(TopBar(back_btn, delete_btn))

        # *Note Screen Container-----------------------------------------------
        self.note_container = BoxLayout(orientation="vertical",
                                        spacing=2,
                                        padding=[5])

        # *Note Name-----------------------------------------------------------

        #       Name Text Input
        self.note_name_ti = CustomTextInput(hint_text="Untitled",
                                            font_size=18,
                                            multiline=False,
                                            write_tab=False,
                                            size_hint=(1, .09),
                                            padding=(10, 10))

        self.note_container.add_widget(self.note_name_ti)
        self._name = 'Untitled'  # This is the default title for notes

        # *Note Body-----------------------------------------------------------
        body_container = BoxLayout()

        #       The ScrollView
        self.body_scroll = ScrollView(size_hint=(1, 1),
                                      size=(1, 1),
                                      bar_color=app_settings.text_color,
                                      bar_pos_y='right', )

        #       Body TextInput Widget
        self.notebody_textinput = CustomTextInput(hint_text="Enter note body",
                                                  multiline=True,
                                                  size_hint_y=None,
                                                  padding=(10, 10))

        # Bind the two widgets to the greater height
        self.body_scroll.bind(height=self.textinput_height)
        self.notebody_textinput.bind(minimum_height=self.textinput_height)

        self.body_scroll.add_widget(self.notebody_textinput)

        body_container.add_widget(self.body_scroll)

        self.note_container.add_widget(body_container)

        # *Pack----------------------------------------------------------------
        self.editnote_container.add_widget(self.note_container)
        self.add_widget(self.editnote_container)

        # *Load on enter, save on exit-----------------------------------------
        self.bind(on_enter=self.load,
                  on_pre_leave=self.save)

    def back(self, *args):
        """Method for back button, saves the note."""

        sm.current = 'notebook'

    def save(self, *args):
        """Save the note."""

        if self.notebody_textinput.text.strip() != '':

            if self.note_name_ti.text != '':

                self._name = self.note_name_ti.text

            if app_variables.active_note is None:  # If we're adding a new note

                # Add note to database
                note_manager.new_obj(self._name,
                                     self.notebody_textinput.text.strip(),
                                     app_variables.active_notebook)

            else:  # If we're editing an existing

                note_manager.update_obj(app_variables.active_note,
                                        name=self._name,
                                        data=self.notebody_textinput.text)

            self.note_name_ti.text = ''
            self.notebody_textinput.text = ''

            # Update note list
            app_variables.notes = note_manager.load()

    def load(self, *args):
        """
        Loads data and populates TextInput widgets.

        I had to take away the y hint to use the ScrollView Widget, which led
        to a crappy resizing while typing behavior. Working on a better
        solution.
        """

        if app_variables.active_note is not None:

            # Fill the TextInputs with the note data
            self.note_name_ti.text = app_variables.get_note_obj(
                app_variables.active_note)[1]
            self.notebody_textinput.text = app_variables.get_note_obj(
                app_variables.active_note)[3]

        else:

            self.note_name_ti.text = ''  # New note
            self.notebody_textinput.text = ''

    def delete(self, *args):
        """Deletes Note."""

        if app_variables.active_note is not None:  # If this isn't a new note

            note_manager.delete(app_variables.active_note)

            app_variables.notes = note_manager.load()
            app_variables.active_note = None

            # Hacky workaround to deal with save method
            self.notebody_textinput.text = ''

        sm.current = 'notebook'

    def textinput_height(self, *args):

        max_var = max(self.notebody_textinput.minimum_height,
                      self.body_scroll.height)
        self.notebody_textinput.height = max_var


class SettingsScreen(Screen):
    """A screen for editing the App Settings."""

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        textinput_color = app_settings.textinput_color
        bg_color = app_settings.app_bg_color

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
                          background_color=bg_color,
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
                              size_hint=(1, .15))

        self.primary_ti = CustomTextInput(text=str(app_settings.text_color),
                                          multiline=False,
                                          size_hint=(1, .15))

        #       Bind
        self.settings_cntnr.add_widget(primary_label)
        self.settings_cntnr.add_widget(self.primary_ti)

        #       Background Color-----------------------------------------------
        secondary_label = Label(text='App Background Color: ',
                                color=app_settings.text_color,
                                size_hint=(1, .15))
        self.secondary_ti = CustomTextInput(text=str(bg_color),
                                            multiline=False,
                                            size_hint=(1, .15))
        #       Bind
        self.settings_cntnr.add_widget(secondary_label)
        self.settings_cntnr.add_widget(self.secondary_ti)

        #       TextInput------------------------------------------------------
        tertiary_label = Label(text='Input Color: ',
                               color=app_settings.text_color,
                               size_hint=(1, .15))
        self.tertiary_ti = CustomTextInput(text=str(textinput_color),
                                           multiline=False,
                                           size_hint=(1, .15))
        #       Bind
        self.settings_cntnr.add_widget(tertiary_label)
        self.settings_cntnr.add_widget(self.tertiary_ti)

        # *Buffer------------------------------------------------------------
        self.settings_cntnr.add_widget(Label())

        # *Default Button----------------------------------------------------
        self.default_button = Button(text="Reset to Default",
                                     background_normal='',
                                     background_color=bg_color,
                                     color=app_settings.text_color,
                                     size_hint=(1, .5))
        self.default_button.bind(on_release=self.set_default)

        contents_cntnr.add_widget(self.settings_cntnr)
        contents_cntnr.add_widget(self.default_button)

        screen_cntnr.add_widget(contents_cntnr)
        self.add_widget(screen_cntnr)

    def on_color(self, *args):
        print(args)

    def back(self, *args):
        """Method for leaving the screen, saves on exit."""

        self.save()
        sm.current = 'menu'

    def set_default(self, *args):
        """Reverts color fields to default."""

        primary_default = app_variables.default_colors[0]
        secondary_default = app_variables.default_colors[1]
        tertiary_default = app_variables.default_colors[2]

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
app_variables = AppVariables()

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
