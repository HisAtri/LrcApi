#!/usr/bin/env python
# This whole module is just id3 tag part of MusicBrainz Picard
# The idea is to get Musicbrainz's layer on top of mutagen without
# dependancies (like qt)

import logging
import os

import mutagen

from . import file
from . import util
from . import aac
from . import aiff
from . import apev2
from . import asf
from . import dsf
from . import flac
from . import id3
from . import mp4
from . import smf
from . import vorbis
from . import wave

from .file import Artwork, MetadataItem, NotAppendable, AudioFile

__version__ = """0.4.3"""

logger = logging.getLogger("music_tag")
log = logger


def _subclass_spider_dfs(kls, _lst=None):
    if _lst is None:
        _lst = []
    for sub in kls.__subclasses__():
        _subclass_spider_dfs(sub, _lst=_lst)
    _lst.append(kls)
    return _lst


def load_file(file_spec, err='raise'):
    if isinstance(file_spec, mutagen.FileType):
        mfile = file_spec
        filename = mfile.filename
    else:
        filename = file_spec
        if not os.path.exists(filename):
            if os.path.exists(os.path.expanduser(os.path.expandvars(filename))):
                filename = os.path.expanduser(os.path.expandvars(filename))
            elif os.path.exists(os.path.expanduser(filename)):
                filename = os.path.expanduser(filename)
        mfile = mutagen.File(filename, easy=False)

    ret = None

    for kls in _subclass_spider_dfs(file.AudioFile):
        # print("checking against:", kls, kls.mutagen_kls)
        if kls.mutagen_kls is not None and isinstance(mfile, kls.mutagen_kls):
            ret = kls(filename, _mfile=mfile)
            break

    if ret is None and err == 'raise':
        raise NotImplementedError("Mutagen type {0} not implemented"
                                  "".format(type(mfile)))

    return ret


__all__ = ['file', 'util',
           'aac', 'aiff', 'apev2', 'asf', 'dsf', 'flac',
           'id3', 'mp4', 'smf', 'vorbis', 'wave',
           'logger', 'log',
           'Artwork', 'MetadataItem', 'NotAppendable',
           'AudioFile',
           'load_file',
           ]
