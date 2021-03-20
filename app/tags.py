#!/usr/bin/env python

import os
import yaml
from pathlib import Path

class Tags():

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if Path(current_dir + '/../tags.yml').is_file():
            self.tags_file = current_dir + '/../tags.yml'
        if Path('/config/tags.yml').is_file():
            self.tags_file = '/config/tags.yml'
        self.last_updated = ''

    def load_tags(self):
        """Load the NFC tag config file if it has changed.
        """
        if (self.last_updated != os.stat(self.tags_file).st_mtime):
            with open(self.tags_file, 'r') as stream:
                self.tags = yaml.load(stream, Loader=yaml.FullLoader)
            self.last_updated = os.stat(self.tags_file).st_mtime
            return self.tags
