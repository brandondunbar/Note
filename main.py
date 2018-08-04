#!/usr/bin/env python3
"""A note keeping app, sorting notes by directory.

Usage:

    python3 main.py

"""

# Modules:
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.textinput import TextInput
from kivy.uix.widget import WidgetException

import pickle

# My scripts:
import note_manager
from note_class import Note


# Redefined widget:
class LabelButton(ButtonBehavior, Label):
    """A Kivy Widget for displaying text, modified for button behavior"""
    def on_press(self):
        sm.current = 'menu'


# App-wide variables:
class Settings:
    """Settings for the app. Allows user defined colors, which change when app
    is reopened."""
    primary_color = [0, 1, 1, 1]  # Can I delete this?
    secondary_color = [0, 0, 0, 1]
    tertiary_color = [.25, .25, .25, 1]

    def __init__(self):
        """Loads color preferences and stores them."""
        self.settings = [[0, 1, 1, 1], [0, 0, 0, 1], [.25, .25, .25, 1]]
        try:
            with open('settings.pickle', "rb") as file_object:
                self.settings = pickle.load(file_object)

        except FileNotFoundError:
            self.save_settings(self.settings)

        self.primary_color = self.settings[0]
        self.secondary_color = self.settings[1]
        self.tertiary_color = self.settings[2]

    def save_settings(self, settings):
        """Saves user settings, when Settings screen is exited.

        Args:
            settings: The array of settings changed, to be saved."""
        with open('settings.pickle', "wb") as file_object:
            pickle.dump(settings, file_object)


class AppVariables:
    """These are essentially global variables, any alternative method is
    welcome."""
    notes = note_manager.load()
    active_notebook = ''
    active_note = ''


# Screens:
class MenuScreen(Screen):
    """The uppermost screen in an hierarchical view, shows on load."""

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.menu = BoxLayout(orientation="vertical",
                              spacing=5)

        # *Top Bar-------------------------------------------------------------
        bar = BoxLayout(orientation="horizontal",
                        size_hint=(1, .1))
        #       New Button
        note_btn = Button(text="+",
                          background_normal='',
                          background_color=app_settings.secondary_color,
                          color=app_settings.primary_color,
                          size_hint=(.15, 1),
                          id="New")
        note_btn.bind(on_release=self.switch_screen)
        bar.add_widget(note_btn)

        #       App title
        bar.add_widget(LabelButton(text="Note",
                                   font_size=25,
                                   color=app_settings.primary_color))

        #       Settings Button
        settings_btn = Button(text="*",
                              background_normal='',
                              background_color=app_settings.secondary_color,
                              color=app_settings.primary_color,
                              size_hint=(.15, 1),
                              id='Settings')
        settings_btn.bind(on_release=self.switch_screen)
        bar.add_widget(settings_btn)
        self.menu.add_widget(bar)

        self.notebooks = BoxLayout(orientation='vertical',
                                   spacing=2,
                                   size_hint_y=None)
        self.notebooks.bind(minimum_height=self.notebooks.setter('height'))

        self.nb_scroll = ScrollView(size_hint=(1, 1),
                                    size=(1, 1),
                                    bar_color=app_settings.primary_color,
                                    bar_pos_y='right')
        self.nb_scroll.add_widget(self.notebooks)
        self.menu.add_widget(self.nb_scroll)

        # Pack
        self.add_widget(self.menu)

        # Load notebooks
        self.bind(on_enter=self.load)

    def switch_screen(self, *args):
        """A method for switching screens.

        Args:
            args[0]: The button object selected, passed automatically."""
        if args[0].id == 'New':
            AppVariables.active_notebook = ''
            sm.current = 'newnotebook'
        elif args[0].id == 'Settings':
            sm.current = 'settings'
        else:
            AppVariables.active_notebook = args[0].id
            sm.current = 'notebook'

    def load(self, *args):
        """Loads all notebooks when screen loads."""
        AppVariables.active_notebook = ''
        AppVariables.active_note = ''
        self.notebooks.clear_widgets()
        if len(AppVariables.notes.items()) > 0:
            for notebook_name, notebook in AppVariables.notes.items():
                notebook_btn = Button(text=notebook_name,
                                      size_hint=(1, None),
                                      background_normal='',
                                      background_color=app_settings.tertiary_color,
                                      color=app_settings.primary_color,
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

    def __init__(self, **kwargs):
        super(NewNotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        menu = BoxLayout(orientation="vertical",
                         padding=[1])

        # *Top Bar-------------------------------------------------------------
        bar = BoxLayout(orientation="horizontal",
                        size_hint=(1, .1))
        #       App title
        bar.add_widget(LabelButton(text="Note",
                                   font_size=25,
                                   color=app_settings.primary_color))
        menu.add_widget(bar)

        #       Buffer
        menu.add_widget(Label(text="",
                              size_hint=(1, .5)))

        # *Notebook Name Entry-------------------------------------------------
        self.nb_name = TextInput(hint_text="Notebook Name...",
                                 multiline=False,
                                 size_hint=(1, .085),
                                 background_active='',
                                 background_normal='',
                                 background_color=app_settings.tertiary_color)
        menu.add_widget(self.nb_name)

        #       Buffer
        menu.add_widget(Label(text="",
                              size_hint=(1, .5)))

        # *Save Button---------------------------------------------------------
        save_btn = Button(text='Save',
                          size_hint=(1, .2),
                          color=app_settings.primary_color,
                          background_color=app_settings.tertiary_color,)
        save_btn.bind(on_release=self.save)
        menu.add_widget(save_btn)

        # Pack
        self.add_widget(menu)

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

    def __init__(self, **kwargs):
        super(NotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.notebook_cntnr = BoxLayout(orientation="vertical",
                                        padding=[1])

        # *Top Bar-------------------------------------------------------------
        bar = BoxLayout(orientation="horizontal",
                        size_hint=(1, .1))
        #       New Button
        note_btn = Button(text="+",
                         background_normal='',
                         background_color=app_settings.secondary_color,
                         color=app_settings.primary_color,
                         size_hint=(.15, 1),
                         id="New")
        note_btn.bind(on_release=self.switch_screen)
        bar.add_widget(note_btn)

        #       App title
        bar.add_widget(LabelButton(text="Note",
                                   font_size=25,
                                   color=app_settings.primary_color))

        #       Settings Button
        delete_btn = Button(text="|||",
                            background_normal='',
                            background_color=app_settings.secondary_color,
                            color=app_settings.primary_color,
                            size_hint=(.15, 1))
        delete_btn.bind(on_release=self.delete)
        bar.add_widget(delete_btn)
        self.notebook_cntnr.add_widget(bar)

        # *Active Notebook Label-----------------------------------------------
        self.current_notebook = Label(text=AppVariables.active_notebook,
                                      color=app_settings.tertiary_color,
                                      size_hint=(1, .1))
        self.notebook_cntnr.add_widget(self.current_notebook)
        self.no_note_lbl = Label(text="No notes to display")

        # *Note Container------------------------------------------------------
        self.notes = BoxLayout(orientation="vertical",
                               spacing=1)
        self.notebook_cntnr.add_widget(self.notes)

        # Pack
        self.add_widget(self.notebook_cntnr)
        # Update widgets on screen entry
        self.bind(on_enter=self.update_widgets)

    def switch_screen(self, *args):
        """A method for switching screens.

        Args:
            args[0]: The button object selected, passed
            automatically.
            args[1]: A Note object. Not passed if it's a new note."""
        if args[0].id == 'new':
            sm.current = 'newnote'
        else:
            try:
                AppVariables.active_note = args[1]
            except IndexError:
                pass
            sm.current = 'editnote'

    def update_widgets(self, *args):
        """Updates the """
        def new_note_btn(note):
            new_note_btn = Button(text=note.name,
                                  size_hint=(1, .1),
                                  background_normal='',
                                  background_color=app_settings.tertiary_color,
                                  color=app_settings.primary_color)
            new_note_btn.bind(on_press=lambda button:
                              self.switch_screen(button, note))
            return new_note_btn

        self.current_notebook.text = AppVariables.active_notebook
        self.current_notebook.color = app_settings.tertiary_color

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


class NoteScreen(Screen):
    def __init__(self, **kwargs):
        super(NoteScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.note_cntnr = BoxLayout(orientation="vertical",
                                    spacing=1)

        # *Top Bar-------------------------------------------------------------
        bar = BoxLayout(orientation="horizontal",
                        size_hint=(1, .1))
        #       Back Button
        back_btn = Button(text="<-",
                          background_normal='',
                          background_color=app_settings.secondary_color,
                          color=app_settings.primary_color,
                          size_hint=(.15, 1),
                          id="Back")
        back_btn.bind(on_release=self.back)
        bar.add_widget(back_btn)

        #       App title
        bar.add_widget(LabelButton(text="Note",
                                   font_size=25,
                                   color=app_settings.primary_color))

        #       Settings Button
        delete_btn = Button(text="|||",
                            background_normal='',
                            background_color=app_settings.secondary_color,
                            color=app_settings.primary_color,
                            size_hint=(.15, 1))
        bar.add_widget(delete_btn)
        delete_btn.bind(on_release=self.delete)
        self.note_cntnr.add_widget(bar)

        # *Current Notebook Label----------------------------------------------
        self.current_notebook = Label(text=AppVariables.active_notebook,
                                      color=app_settings.tertiary_color,
                                      size_hint=(1, .1))
        self.note_cntnr.add_widget(self.current_notebook)

        # *Note Name-----------------------------------------------------------
        self.note_name_ti = TextInput(hint_text="Name...",
                                      multiline=False,
                                      write_tab=False,
                                      size_hint=(1, .06),
                                      background_active='',
                                      background_normal='',
                                      background_color=
                                      app_settings.tertiary_color)
        self.note_cntnr.add_widget(self.note_name_ti)

        # *Note Body-----------------------------------------------------------
        self.note_body_ti = TextInput(hint_text="Enter note body...",
                                      multiline=True,
                                      size_hint_y=None,
                                      background_active='',
                                      background_normal='',
                                      background_color=app_settings.tertiary_color)

        self.note_body_ti.bind(minimum_height=
                               self.note_body_ti.setter('height'))

        self.body_scroll = ScrollView(size_hint=(1, 1),
                                      size=(1, 1),
                                      bar_color=app_settings.primary_color,
                                      bar_pos_y='right')
        self.body_scroll.add_widget(self.note_body_ti)

        self.note_cntnr.add_widget(self.body_scroll)

        # *Pack----------------------------------------------------------------
        self.add_widget(self.note_cntnr)

        # *Edit or New?--------------------------------------------------------
        self.bind(on_enter=self.load)

    def back(self, *args):
        """Method for back button, saves the note. Should I make a separate
        method for saving, that is called by this one?"""
        if self.note_name_ti.text != '' and self.note_body_ti.text != '':
            # Assign list of notes to variable for readability
            notebook = AppVariables.notes[AppVariables.active_notebook]

            if AppVariables.active_note == '':  # If we're adding a new note
                note = Note(name=self.note_name_ti.text,
                            body=self.note_body_ti.text.strip())
                notebook.append(note)

            else:  # If we're editing an existing
                # Find note and overwrite it
                for index, item in enumerate(notebook):
                    if item.name.strip() == AppVariables.active_note.name:
                        notebook[index].name = self.note_name_ti.text
                        notebook[index].body = self.note_body_ti.text.strip()

            # Not in a note, set active note to blank
            AppVariables.active_note = ''

            self.note_name_ti.text = ''
            self.note_body_ti.text = ''

            note_manager.save(AppVariables.notes)
            sm.current = 'notebook'
        else:  # Called if either text input box is empty
            print("Empty")

    def load(self, *args):
        """
        Loads data and populates TextInput widgets.

        Blank lines are added to the end because to implement the scrollbar
        I had to take away the y hint, which led to a crappy resizing while
        typing behavior, so I decided this is the better alternative
        """
        self.current_notebook.text = AppVariables.active_notebook
        self.current_notebook.color = app_settings.tertiary_color
        if AppVariables.active_note != '':
            self.note_name_ti.text = AppVariables.active_note.name
            self.note_body_ti.text = AppVariables.active_note.body + '\n'*25
        else:
            self.note_name_ti.text = ''  # New note
            self.note_body_ti.text = '\n'*25

    def delete(self, *args):
        """Deletes Note. If it's a new note, should we clear the TextInput
        widgets?"""
        if AppVariables.active_note != '':  # If this isn't a new note
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
                AppVariables.active_note = ''
                sm.current = 'notebook'


class SettingsScreen(Screen):
    """A screen for editing the App Settings."""

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        screen_cntnr = BoxLayout(orientation='vertical',
                                 spacing=5)
        self.settings_cntnr = GridLayout(cols=2,
                                         spacing=1)

        # *Top Bar-------------------------------------------------------------
        bar = BoxLayout(orientation="horizontal",
                        size_hint=(1, .1))
        #       Back Button
        back_btn = Button(text="<-",
                          background_normal='',
                          background_color=app_settings.secondary_color,
                          color=app_settings.primary_color,
                          size_hint=(.15, 1),
                          id="Back")
        back_btn.bind(on_release=self.back)
        bar.add_widget(back_btn)

        #       App title
        bar.add_widget(LabelButton(text="Note",
                                   font_size=25,
                                   color=app_settings.primary_color))

        #       Settings Button
        placeholder = Button(background_color=app_settings.secondary_color,
                             background_normal='',
                             color=app_settings.primary_color,
                             size_hint=(.15, 1))
        bar.add_widget(placeholder)
        screen_cntnr.add_widget(bar)

        # *Message Label-------------------------------------------------------
        self.msg_lbl = Label(text='Changes will take effect when program'
                                  ' opens next.')
        self.add_widget(self.msg_lbl)

        # *Colors--------------------------------------------------------------
        #       Primary
        primary_label = Label(text='Primary Color: ',
                              color=app_settings.primary_color,
                              size_hint=(1, .085))
        self.primary_ti = TextInput(text=str(app_settings.primary_color),
                                    multiline=False,
                                    size_hint=(1, .085),
                                    background_active='',
                                    background_normal='',
                                    background_color=app_settings.tertiary_color)
        #       Bind
        self.settings_cntnr.add_widget(primary_label)
        self.settings_cntnr.add_widget(self.primary_ti)

        #       Secondary
        secondary_label = Label(text='Secondary Color: ',
                                color=app_settings.primary_color,
                                size_hint=(1, .085))
        self.secondary_ti = TextInput(text=str(app_settings.secondary_color),
                                      multiline=False,
                                      size_hint=(1, .085),
                                      background_active='',
                                      background_normal='',
                                      background_color=app_settings.tertiary_color)
        #       Bind
        self.settings_cntnr.add_widget(secondary_label)
        self.settings_cntnr.add_widget(self.secondary_ti)

        #       Tertiary
        tertiary_label = Label(text='Tertiary Color: ',
                               color=app_settings.primary_color,
                               size_hint=(1, .085))
        self.tertiary_ti = TextInput(text=str(app_settings.tertiary_color),
                                     multiline=False,
                                     size_hint=(1, .085),
                                     background_active='',
                                     background_normal='',
                                     background_color=app_settings.tertiary_color)
        #       Bind
        self.settings_cntnr.add_widget(tertiary_label)
        self.settings_cntnr.add_widget(self.tertiary_ti)

        #       Buffer
        self.settings_cntnr.add_widget(Label(text=""))

        screen_cntnr.add_widget(self.settings_cntnr)
        self.add_widget(screen_cntnr)

    def back(self, *args):
        """Method for leaving the screen, saves on exit."""
        def parse_color(color):
            """Converts string to list to be stored.

            Args:
                color: The string (r, g, b, s) to be converted

            Returns:
                A usable list representing a color, to be used by Kivy."""
            color_list = [float(value) for value in color[1:-1].split(",")]
            return color_list
        settings = []

        try:
            settings.append(parse_color(self.primary_ti.text))
        except ValueError:
            settings.append(app_settings.primary_color)
        try:
            settings.append(parse_color(self.secondary_ti.text))
        except ValueError:
            settings.append(app_settings.secondary_color)
        try:
            settings.append(parse_color(self.tertiary_ti.text))
        except ValueError:
            settings.append(app_settings.tertiary_color)
        app_settings.save_settings(settings)
        sm.current = 'menu'


# Instantiate settings for them to take effect
app_settings = Settings()

# Screen Manager object manages which screen is visible
sm = ScreenManager(transition=NoTransition())
screens = [MenuScreen(name='menu'),
           NotebookScreen(name='notebook'),
           NewNotebookScreen(name='newnotebook'),
           NoteScreen(name="editnote"),
           SettingsScreen(name="settings")]

for screen in screens:
    sm.add_widget(screen)


class NoteApp(App):
    """Represents the application itself, Window settings modified here."""

    def build(self):
        # I don't want a white window background
        Window.clearcolor = app_settings.secondary_color
        Window.size = (500, 550)  # Set window size
        return sm  # Return screen manager, runs app


if __name__ == '__main__':
    NoteApp().run()
