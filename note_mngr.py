"""
Brandon Dunbar
A script to load/save notes dictionary
7.24.18
"""

import pickle


def load():
    """
    Deserializes the note dictionary
    :return: Note dictionary
    """

    try:
        with open('serial_notes.pickle', "rb") as file_object:
            notes = pickle.load(file_object)
            return notes
    except FileNotFoundError:
        print("serial_notes.pickle not found. First run?")
        return {}


def save(notes):
    """
    Takes in a note dictionary in the format:
    {'Notebook Name': [<Note Object>, [...], ], [...]}
    :param notes: The notes dictionary to be saved
    """

    # Serialize
    file_name = "serial_notes.pickle"
    with open(file_name, "wb") as file_object:
        pickle.dump(notes, file_object)
