import unittest
from memdir import MemDir

class TestCreation(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = MemDir('root')

    def test_instantiation(self):
        self.assertEqual(self.dir.name, 'root')
        self.assertIsNone(self.dir.parent)
        self.assertEqual(self.dir.files, [])
        self.assertEqual(self.dir, {})

    def test_create_child_str(self):
        self.dir.create_child('child')
        self.assertEqual(list(self.dir.keys()), ['child'])
        self.assertIsInstance(self.dir['child'], MemDir)

    def test_create_child_memdir(self):
        child = MemDir('child1')
        self.dir.create_child(child)
        self.assertEqual(list(self.dir.keys()), ['child1'])

    def test_add_obj(self):
        self.dir.add_obj([1,2,3,4])
        self.assertListEqual(self.dir.files, [[1,2,3,4]])

class TestUseCase(unittest.TestCase):
    def setUp(self) -> None:
        memdir = MemDir('.')
        memdir.make_subdirs('child1/child11')
        memdir.make_subdirs('child2/child22/deep/deeper')
        memdir.make_subdirs('child2/child22/deep1/deeper')
        memdir.make_subdirs('child2/child22/deep2')
        memdir['child1'].add_obj([1, 2, 3, 4])
        # memdir['child2/child22'].rename('CHILD22')
        memdir['child1/child11'].add_obj('a string')
        memdir['child1/child11'].add_obj(['a', 'list', 'of', (1, 2, 3)])
        child = memdir['child1/child11']
        memdir['child1'].add_objs([1, 2, 3, 4])
        self.memdir = memdir

    def test_getitem_dirname(self):
        self.assertIs(
            self.memdir['child2/child22/deep'],
            self.memdir['child2']['child22']['deep']
        )

    def test_getitem_filenum(self):
        pass

    def test_get_path(self):
        child = self.memdir['child2/child22/deep']
        self.assertEqual(child.get_path(), './child2/child22/deep')

    def test_rename_child(self):
        self.memdir['child2/child22'].rename('CHILD22')
        self.assertIn('CHILD22', self.memdir['child2'])
        self.assertNotIn('child22', self.memdir['child2'])
        self.assertIs(self.memdir['child2/CHILD22'].parent, self.memdir['child2'])

    def test_copy_of_node_paste_as_different_subdir(self):
        nodecopy = self.memdir['child1/child11'].copy(newname='child11copy')
        nodecopy[1][1] = 'tuple'
        # nodecopy.rename('child11copy')
        self.memdir['child2/child22/deep'].create_child(nodecopy)
        self.assertEqual(self.memdir['child2/child22/deep/child11copy'], nodecopy)
        self.assertEqual(self.memdir['child1/child11'][1], ['a', 'list', 'of', (1, 2, 3)])

if __name__ == '__main__':
    unittest.main()
