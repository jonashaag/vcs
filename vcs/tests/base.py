"""
Module providing backend independent mixin class. It requires that
InMemoryChangeset class is working properly at backend class.
"""
import os
import vcs
import time
import shutil
import datetime
from vcs.utils.compat import unittest

from conf import SCM_TESTS, get_new_dir

from vcs.nodes import FileNode


class BackendTestMixin(object):
    """
    This is a backend independent test case class which should be created
    with ``type`` method.

    It is required to set following attributes at subclass:

    - ``backend_alias``: alias of used backend (see ``vcs.BACKENDS``)
    - ``repo_path``: path to the repository which would be created for set of
      tests
    - ``recreate_repo_per_test``: If set to ``False``, repo would NOT be created
      before every single test. Defaults to ``True``.
    """
    recreate_repo_per_test = True

    @classmethod
    def get_backend(cls):
        return vcs.get_backend(cls.backend_alias)

    @classmethod
    def _get_commits(cls):
        commits = [
            {
                'message': 'Initial commit',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('foobar', content='Foobar'),
                    FileNode('foobar2', content='Foobar II'),
                    FileNode('foo/bar/baz', content='baz here!'),
                ],
            },
            {
                'message': 'Changes...',
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21),
                'added': [
                    FileNode('some/new.txt', content='news...'),
                ],
                'changed': [
                    FileNode('foobar', 'Foobar I'),
                ],
                'removed': [],
            },
        ]
        return commits

    @classmethod
    def setUpClass(cls):
        Backend = cls.get_backend()
        cls.backend_class = Backend
        cls.repo_path = get_new_dir(str(time.time()))
        cls.repo = Backend(cls.repo_path, create=True)
        cls.imc = cls.repo.in_memory_changeset

        for commit in cls._get_commits():
            for node in commit.get('added', []):
                cls.imc.add(FileNode(node.path, content=node.content))
            for node in commit.get('changed', []):
                cls.imc.change(FileNode(node.path, content=node.content))
            for node in commit.get('removed', []):
                cls.imc.remove(FileNode(node.path))
            cls.tip = cls.imc.commit(message=commit['message'],
                author=commit['author'],
                date=commit['date'])

    @classmethod
    def tearDownClass(cls):
        if not getattr(cls, 'recreate_repo_per_test', False) and \
            'VCS_REMOVE_TEST_DIRS' in os.environ:
            shutil.rmtree(cls.repo_path)

    def setUp(self):
        if getattr(self, 'recreate_repo_per_test', False):
            self.__class__.setUpClass()

    def tearDown(self):
        if getattr(self, 'recreate_repo_per_test', False) and \
            'VCS_REMOVE_TEST_DIRS' in os.environ:
            shutil.rmtree(self.repo_path)



# For each backend create test case class
for alias in SCM_TESTS:
    attrs = {
        'backend_alias': alias,
    }
    cls_name = ''.join(('%s base backend test' % alias).title().split())
    bases = (BackendTestMixin, unittest.TestCase)
    globals()[cls_name] = type(cls_name, bases, attrs)


if __name__ == '__main__':
    unittest.main()

