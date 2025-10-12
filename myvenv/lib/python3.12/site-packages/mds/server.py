import os
import subprocess
import sys
from bottle import request, response, route, post, run, template, static_file
from .markdown import get_markdown_files, search_markdown_files

class Templates:
    """
    Very simple data class to perform a small path manipulation on the templates
    allows easy access of templates in the route creation process and allows decoupling
    still not sure this is the best implementation of this but trying it for now
    """
    def __init__(self, assets_path):
        self.assets_path = assets_path

        self.main_layout = f"{self.assets_path}/views/main_layout.tpl"
        self.nav = f"{self.assets_path}/views/nav.tpl"
        self.home_content = f"{self.assets_path}/views/home_content.tpl"
        self.home_bar = f"{self.assets_path}/views/home_bar.tpl"
        # self.editor = f"{self.assets_path}/views/editor.tpl"
        self.markdown_content = f"{self.assets_path}/views/markdown_content.tpl"
        self.markdown_content_bar = f"{self.assets_path}/views/markdown_content_bar.tpl"
        self.markdown_editor = f"{self.assets_path}/views/markdown_editor.tpl"
        self.markdown_editor_bar = f"{self.assets_path}/views/markdown_editor_bar.tpl"

def refresh_markdown_files(notepath):
    return get_markdown_files(notepath)


def create_routes(assets_path, notepath, templates):

    @route('/')
    def index():
        markdown_files = refresh_markdown_files(notepath)
        return template(
                templates.main_layout,
                md=markdown_files, 
                nav=templates.nav,
                content=templates.home_content,
                bar=templates.home_bar,
                title="Home")

    @route('/<note>')
    def r(note):
        try:
            markdown_files = refresh_markdown_files(notepath)
            markdown_file = search_markdown_files(note, markdown_files)
            rendered_markdown_note = markdown_file.render()
            return template(
                    templates.main_layout,
                    rendered_markdown=rendered_markdown_note,
                    f=markdown_file,
                    md=markdown_files,
                    nav=templates.nav,
                    content=templates.markdown_content,
                    bar=templates.markdown_content_bar,
                    title=markdown_file.pretty_filename)
        except IndexError as e:
            print(e, file=sys.stderr)
            return "404: File Not Found"

    @route('/static/<filename>')
    @route('/mde/static/<filename>')
    def server_static(filename):
        return static_file(
                filename, 
                root=f'{assets_path}/static')


    @route("/mde/<note>")
    def mde_note_edit(note):
        markdown_files = refresh_markdown_files(notepath)
        markdown_file = search_markdown_files(note, markdown_files)
        read_markdown_note = markdown_file.read()
        return template(
                templates.main_layout,
                info=read_markdown_note, 
                f=markdown_file,
                md=markdown_files,
                nav=templates.nav,
                content=templates.markdown_editor,
                bar=templates.markdown_editor_bar,
                title=f"Editing {markdown_file.pretty_filename}")

    @post("/mde/new")
    def new_note():
        data = request.json
        new_note_name = data['note_name']
        print(new_note_name)
        filepath = notepath + "/" + new_note_name
        print(filepath)
        with open(filepath, 'w') as f:
            f.write("")
        return {}

    @post("/mde/save")
    def save_note():
        try:
            data = request.json
            absolute_path = data['absolute_path']
            updated_file_content = data['saved_value']
            with open(absolute_path, 'w') as f:
                f.writelines(updated_file_content)
            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False}

    @post("/mde/delete")
    def delete_note():
        try:
            ### todo 
            ### refresh file contents for main page so the file list is updated
            data = request.json
            absolute_path = data['absolute_path']
            os.remove(absolute_path)
            return {"success": True}
        except Exception as e:
            print(e)
            return {"success": False}

    @post("/tester")
    def tester():
        response.content_type = "application/json"
        return response

def start_server(c):
    templates = Templates(c.assets_path)
    create_routes(c.assets_path, c.notepath, templates)
    if c.daemonize:
        subprocess.Popen(["mds", "/home/sdixon/Dropbox/notes"])
    else:
        run(host=c.host, port=c.port, reloader=c.debug)


