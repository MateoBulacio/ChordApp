from flask import redirect, session
from functools import wraps


def login_required(f):
    """Decorator to require login for routes.

    Redirects unauthenticated users to the login page.

    Args:
        f: The function to decorate.

    Returns:
        callable: The decorated function.

    See Also:
        https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function



def parse_content(content):
    """Parses chord notations from the given content string.

    Processes the input to extract chords (in brackets), lyrics, spaces, and line breaks,
    returning a structured list for rendering.

    Args:
        content: The raw song content string with chords and lyrics.

    Returns:
        list[dict[str, str]]: A list of dictionaries, each with 'type' ('chord', 'lyric', 'spaces', 'line-break')
            and 'value' keys.

    Examples:
        >>> parse_content("[C]Hello world\\n")
        [{'type': 'spaces', 'value': ' '}, {'type': 'chord', 'value': 'C'}, {'type': 'spaces', 'value': ' '},
         {'type': 'lyric', 'value': 'Hello world'}, {'type': 'line-break', 'value': '\\n'}]
    """

    # Data structure: 
    # List of dictionaries with 'type' and 'value' keys; types: 'chord', 'lyric', 'spaces' and 'line-break'. All values are strings. 

    parsed_song = []
    cursor = 0
    for c in content:
        if c == " ":
            # Count consecutive spaces
            space_count = 0
            while cursor < len(content) and content[cursor] == " ":
                space_count += 1
                cursor += 1
            parsed_song.append({"type": "spaces", "value": " " * space_count})
        elif c == "[":
            # Extract chord
            chord = ""
            cursor += 1
            while cursor < len(content) and content[cursor] != "]":
                chord += content[cursor]
                cursor += 1
            parsed_song.append({"type": "spaces", "value": " "})
            parsed_song.append({"type": "chord", "value": chord})
            parsed_song.append({"type": "spaces", "value": " "})
            cursor += 1  # Skip the closing bracket
        elif c == "\n":
            parsed_song.append({"type": "line-break", "value": "\n"})
            cursor += 1
        else:
            # Extract lyric
            lyric = ""
            while cursor < len(content) and content[cursor] not in [" ", "[", "]", "\n"]:
                lyric += content[cursor]
                cursor += 1
            parsed_song.append({"type": "lyric", "value": lyric})

    return parsed_song

