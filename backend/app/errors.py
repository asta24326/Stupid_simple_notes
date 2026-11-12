class NoteError(Exception):
    """Base class for all domain errors of the notes application."""


class EmptyTextError(NoteError):
    """Raised when the note text is an empty string."""


class TextTooLongError(NoteError):
    """Raised when the note text is longer than the allowed maximum."""


class NoteNotFoundError(NoteError):
    """Raised when a note with the requested id does not exist."""