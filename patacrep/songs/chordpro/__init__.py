"""Chordpro parser"""

from jinja2 import Environment, FileSystemLoader, contextfunction
import pkg_resources
import os

from patacrep import encoding, files
from patacrep.songs import Song, search_image
from patacrep.songs.chordpro.syntax import parse_song
from patacrep.templates import Renderer

class ChordproSong(Song):
    """Chordpros song parser."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jinjaenv = None

    def parse(self, config):
        """Parse content, and return the dictionary of song data."""
        with encoding.open_read(self.fullpath, encoding=self.encoding) as song:
            song = parse_song(song.read(), self.fullpath)
        self.authors = song.authors
        self.titles = song.titles
        self.languages = song.get_data_argument('language', [self.config['lang']])
        self.data = song.meta
        self.cached = {
            'song': song,
            }

    def render(self, output, output_format):
        context = {
            'language': self.languages[0],
            "path": files.relpath(self.fullpath, os.path.dirname(output)),
            "titles": self.titles,
            "authors": self.authors,
            "metadata": self.data,
            "render": self._render_ast,
            "config": self.config,
            }
        self.jinjaenv = Environment(loader=FileSystemLoader(os.path.join(
            os.path.abspath(pkg_resources.resource_filename(__name__, 'data')),
            output_format,
            )))
        self.jinjaenv.filters['search_image'] = search_image
        return self._render_ast(
            context,
            self.cached['song'].content,
            template="song",
            )

    @contextfunction
    def _render_ast(self, context, content, template=None):
        """Render ``content``."""
        if isinstance(context, dict):
            context['content'] = content
        else:
            context.vars['content'] = content
        if template is None:
            template = content.template()
        return Renderer(
            template=template,
            encoding='utf8',
            jinjaenv=self.jinjaenv,
            ).template.render(context)

SONG_PARSERS = {
    'sgc': ChordproSong,
    }