"""Directory Manager Tests."""

import os
import unittest
from core.dir_manager import DirectoryManagerUtils


class DirectoryManagerUtilsTest(unittest.TestCase):

    def test_ensure_dir_struct(self):

        DirectoryManagerUtils.ensure_dir_struct('data/utd')
        self.assertTrue(os.path.exists('data/utd'))
