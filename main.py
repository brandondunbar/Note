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


class TopBar(BoxLayout):
    def __init__(self, button1=None, button2=None, **kwargs):
        super(TopBar, self).__init__(**kwargs)

        # print(Window.size)
        self.size_hint_y = .1
        buttons = []

        if button1:
            buttons.append(button1)
        else:
            blank_button = Button(background_normal='',
                                  background_down='',
                                  background_color=app_settings.color2,
                                  size_hint=(.15, 1))
            buttons.append(blank_button)

        if button2:
            buttons.append(button2)
        else:
            blank_button = Button(background_normal='',
                                  background_down='',
                                  background_color=app_settings.color2,
                                  size_hint=(.15, 1))
            buttons.append(blank_button)

        for button in buttons:

            button.background_normal = ''
            button.background_color = app_settings.color2
            button.color = app_settings.color1
            button.size_hint = (.15, 1)

        title = LabelButton(text="Note",
                            font_size=25,
                            color=app_settings.color1)

        self.add_widget(buttons[0])
        self.add_widget(title)
        self.add_widget(buttons[1])


# App-wide variables:
class Settings:
    """Settings for the app. Allows user defined colors, which change when app
    is reopened."""
    color1 = [0, 1, 1, 1]  # Can I delete this?
    color2 = [0, 0, 0, 1]
    color3 = [.25, .25, .25, 1]

    def __init__(self):
        """Loads color preferences and stores them."""
        self.settings = [[0, 1, 1, 1], [0, 0, 0, 1], [.25, .25, .25, 1]]
        try:
            with open('settings.pickle', "rb") as file_object:
                self.settings = pickle.load(file_object)

        except FileNotFoundError:
            self.save_settings(self.settings)

        self.color1 = self.settings[0]
        self.color2 = self.settings[1]
        self.color3 = self.settings[2]

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
    active_notebook = None
    active_note = None


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
                                    bar_color=app_settings.color1,
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
                                      background_color=app_settings.color3,
                                      color=app_settings.color1,
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
        screen_container = BoxLayout(orientation="vertical",
                                     padding=[1])

        # *Top Bar-------------------------------------------------------------
        screen_container.add_widget(TopBar())

        #       Buffer
        content_container = BoxLayout(orientation='vertical')
        content_container.add_widget(Label(text="",
                                           size_hint=(1, .5)))

        # *Notebook Name Entry-------------------------------------------------
        self.nb_name = TextInput(hint_text="Notebook Name...",
                                 multiline=False,
                                 size_hint=(1, .085),
                                 background_active='',
                                 background_normal='',
                                 background_color=app_settings.color3)
        content_container.add_widget(self.nb_name)

        #       Buffer
        content_container.add_widget(Label(text="",
                                           size_hint=(1, .5)))

        # *Save Button---------------------------------------------------------
        save_btn = Button(text='Save',
                          size_hint=(1, .2),
                          color=app_settings.color1,
                          background_color=app_settings.color3,)
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

    def __init__(self, **kwargs):
        super(NotebookScreen, self).__init__(**kwargs)

        # Container------------------------------------------------------------
        self.notebook_cntnr = BoxLayout(orientation="vertical",
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
        self.notebook_cntnr.add_widget(TopBar(new_btn, delete_btn))

        # *Active Notebook Label-----------------------------------------------
        active_nb = ''
        if AppVariables.active_notebook is not None:
            active_nb = AppVariables.active_notebook

        self.current_notebook = Label(text=active_nb,
                                      color=app_settings.color3,
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
        """Updates the Notebook container"""
        def new_note_btn(note):
            note_btn = Button(text=note.name,
                              size_hint=(1, None),
                              background_normal='',
                              background_color=app_settings.color3,
                              color=app_settings.color1)
            note_btn.bind(on_press=lambda button:
                              self.switch_screen(button, note))
            return note_btn

        self.current_notebook.text = AppVariables.active_notebook
        self.current_notebook.color = app_settings.color3

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
        self.note_container = BoxLayout(orientation="vertical",
                                        spacing=1)

        # *Top Bar-------------------------------------------------------------

        #       Back Button
        back_btn = Button(text="<-",
                          background_normal='',
                          background_color=app_settings.color2,
                          color=app_settings.color1,
                          size_hint=(.15, 1),
                          id="Back")
        back_btn.bind(on_release=self.back)

        #       Settings Button
        delete_btn = Button(text="|||",
                            background_normal='',
                            background_color=app_settings.color2,
                            color=app_settings.color1,
                            size_hint=(.15, 1))
        delete_btn.bind(on_release=self.delete)

        self.note_container.add_widget(TopBar(back_btn, delete_btn))

        # *Current Notebook Label----------------------------------------------
        active_nb = ''
        if AppVariables.active_notebook is not None:
            active_nb = AppVariables.active_notebook

        self.current_notebook = Label(text=active_nb,
                                      color=app_settings.color3,
                                      size_hint=(1, .1))
        self.note_container.add_widget(self.current_notebook)

        # *Note Name-----------------------------------------------------------
        self.note_name_ti = TextInput(hint_text="Name...",
                                      multiline=False,
                                      write_tab=False,
                                      size_hint=(1, .07),
                                      background_active='',
                                      background_normal='',
                                      background_color=
                                      app_settings.color3)
        self.note_container.add_widget(self.note_name_ti)

        # *Note Body-----------------------------------------------------------
        self.note_body_ti = TextInput(hint_text="Enter note body...",
                                      multiline=True,
                                      size_hint_y=None,
                                      background_active='',
                                      background_normal='',
                                      background_color=app_settings.color3)

        self.note_body_ti.bind(minimum_height=
                               self.note_body_ti.setter('height'))

        self.body_scroll = ScrollView(size_hint=(1, 1),
                                      size=(1, 1),
                                      bar_color=app_settings.color1,
                                      bar_pos_y='right')
        self.body_scroll.add_widget(self.note_body_ti)

        self.note_container.add_widget(self.body_scroll)

        # *Pack----------------------------------------------------------------
        self.add_widget(self.note_container)

        # *Edit or New?--------------------------------------------------------
        self.bind(on_enter=self.load)

    def back(self, *args):
        """Method for back button, saves the note. Should I make a separate
        method for saving, that is called by this one?"""
        if self.note_name_ti.text != '' and self.note_body_ti.text != '':
            # Assign list of notes to variable for readability
            notebook = AppVariables.notes[AppVariables.active_notebook]

            if AppVariables.active_note is None:  # If we're adding a new note
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
            AppVariables.active_note = None

            self.note_name_ti.text = ''
            self.note_body_ti.text = ''

            note_manager.save(AppVariables.notes)
            sm.current = 'notebook'
        else:  # Called if either text input box is empty
            sm.current = 'notebook'

    def load(self, *args):
        """
        Loads data and populates TextInput widgets.

        Blank lines are added to the end because to implement the scrollbar
        I had to take away the y hint, which led to a crappy resizing while
        typing behavior, so I decided this is the better alternative
        """
        self.current_notebook.text = AppVariables.active_notebook
        self.current_notebook.color = app_settings.color3
        if AppVariables.active_note is not None:
            self.note_name_ti.text = AppVariables.active_note.name
            self.note_body_ti.text = AppVariables.active_note.body + '\n'*25
        else:
            self.note_name_ti.text = ''  # New note
            self.note_body_ti.text = '\n'*25

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

        #       Back Button
        back_btn = Button(text="<-",
                          background_normal='',
                          background_color=app_settings.color2,
                          color=app_settings.color1,
                          size_hint=(.15, 1),
                          id="Back")
        back_btn.bind(on_release=self.back)

        screen_cntnr.add_widget(TopBar(back_btn))

        # *Message Label-------------------------------------------------------
        self.msg_lbl = Label(text='Changes will take effect when program'
                                  ' opens next.')
        self.add_widget(self.msg_lbl)

        # *Colors--------------------------------------------------------------
        #       Primary
        primary_label = Label(text='Primary Color: ',
                              color=app_settings.color1,
                              size_hint=(1, .085))
        self.primary_ti = TextInput(text=str(app_settings.color1),
                                    multiline=False,
                                    size_hint=(1, .085),
                                    background_active='',
                                    background_normal='',
                                    background_color=app_settings.color3)
        #       Bind
        self.settings_cntnr.add_widget(primary_label)
        self.settings_cntnr.add_widget(self.primary_ti)

        #       Secondary
        secondary_label = Label(text='Secondary Color: ',
                                color=app_settings.color1,
                                size_hint=(1, .085))
        self.secondary_ti = TextInput(text=str(app_settings.color2),
                                      multiline=False,
                                      size_hint=(1, .085),
                                      background_active='',
                                      background_normal='',
                                      background_color=app_settings.color3)
        #       Bind
        self.settings_cntnr.add_widget(secondary_label)
        self.settings_cntnr.add_widget(self.secondary_ti)

        #       Tertiary
        tertiary_label = Label(text='Tertiary Color: ',
                               color=app_settings.color1,
                               size_hint=(1, .085))
        self.tertiary_ti = TextInput(text=str(app_settings.color3),
                                     multiline=False,
                                     size_hint=(1, .085),
                                     background_active='',
                                     background_normal='',
                                     background_color=app_settings.color3)
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
            settings.append(app_settings.color1)
        try:
            settings.append(parse_color(self.secondary_ti.text))
        except ValueError:
            settings.append(app_settings.color2)
        try:
            settings.append(parse_color(self.tertiary_ti.text))
        except ValueError:
            settings.append(app_settings.color3)
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
        Window.clearcolor = app_settings.color2
        Window.size = (500, 550)  # Set window size
        return sm  # Return screen manager, runs app


if __name__ == '__main__':
    NoteApp().run()
