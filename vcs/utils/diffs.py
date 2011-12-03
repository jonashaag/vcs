# -*- coding: utf-8 -*-
# original copyright: 2007-2008 by Armin Ronacher
# licensed under the BSD license.

import re
import difflib
import logging

from difflib import unified_diff
from itertools import tee, imap

from vcs.exceptions import VCSError
from vcs.nodes import FileNode, NodeError


def get_udiff(filenode_old, filenode_new,show_whitespace=True):
    """
    Returns unified diff between given ``filenode_old`` and ``filenode_new``.
    """
    try:
        filenode_old_date = filenode_old.last_changeset.date
    except NodeError:
        filenode_old_date = None

    try:
        filenode_new_date = filenode_new.last_changeset.date
    except NodeError:
        filenode_new_date = None

    for filenode in (filenode_old, filenode_new):
        if not isinstance(filenode, FileNode):
            raise VCSError("Given object should be FileNode object, not %s"
                % filenode.__class__)

    if filenode_old_date and filenode_new_date:
        if not filenode_old_date < filenode_new_date:
            logging.debug("Generating udiff for filenodes with not increasing "
                "dates")

    vcs_udiff = unified_diff(filenode_old.content.splitlines(True),
                               filenode_new.content.splitlines(True),
                               filenode_old.name,
                               filenode_new.name,
                               filenode_old_date,
                               filenode_old_date)
    return vcs_udiff
