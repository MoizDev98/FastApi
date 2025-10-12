from pathlib import Path
import mistune


def get_markdown_files(notepath: str) -> list:
    """
    takes a path of notes, instantiates each note as a class of MarkdownNote,
    returns list of MarkdownNotes
    """
    paths = Path(notepath).rglob("*.md")
    return [MarkdownNote(notepath, path.as_posix(), path.name) for path in paths]


class MarkdownNote:
    """
    Simple data class to more easily work with absolute path names and filenames
    """
    def __init__(self, notepath: str, absolute_path: str, filename:str):
        self.notepath = notepath # Path to the notes given from config
        self.absolute_path = absolute_path # Absolute path to markdown file
        self.filename = filename # Just the filename
        self.pretty_filename = self._get_pretty_name() # Filename with extension stripped
        self.url_path = self._get_url_path() # Relative url path to note
        self.rendered = ""

    def __repr__(self):
        return f"MarkdownNote({self.notepath}, {self.absolute_path}, {self.filename}"

    def _get_pretty_name(self):
        ## Need to make sure this doesn't pop a file without an md tag
        temp = self.filename.split(".")
        return temp[0]

    def _get_url_path(self) -> str:
        s = self.absolute_path.split("/")
        url_path_arr = []
        for i in s:
            if i not in self.notepath:
                url_path_arr.append(i)

        url_path_arr.pop()
        url_path_arr.append(self.pretty_filename)
        return "/".join(url_path_arr)

    def read(self) -> str:
        with open(self.absolute_path, 'r') as markdown_note:
            buf = markdown_note.read()
        return buf


    def render(self) -> str:
        buf = self.read()
        self.rendered = mistune.markdown(buf)
        return self.rendered


def search_markdown_files(note: str, markdown_files: list) -> MarkdownNote:
    ## Return first matching MarkdownNote
    return [f for f in markdown_files if f.pretty_filename == note][0]
