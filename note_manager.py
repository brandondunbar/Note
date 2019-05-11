"""A script that serializes and deserializes a dictionary.

Usage:
    import note_manager
    notes = note_manager.load()
    note_manager.save(notes)
"""

import pickle


def load():
    """Loads the data object stored in serial_notes.pickle in the local
    directory.

    Returns:
        Either the loaded object (typically a dictionary of notes in the format
        {'Notebook Name': [<Note Object>, <Note Object>,], '...':[...],}) or
        an empty dictionary to be used for the same purpose.
    """

    try:
        with open('serial_notes.pickle', "rb") as file_object:
            notes = pickle.load(file_object)
            return notes

    except FileNotFoundError:
        return {}


def save(notes):
    """Serializes an object into the serial_notes.pickle file.

    Args:
        notes: A dictionary object in the format:
        {'Notebook Name': [<Note Object>, <Note Object>,], '...':[...],}
    """

    # Serialize
    file_name = "serial_notes.pickle"
    with open(file_name, "wb") as file_object:
        pickle.dump(notes, file_object)
