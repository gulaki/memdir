import os

path = os.path.dirname(__file__)
EXTN = '.dat'

def loader(file):
    with open(file, 'r') as f:
        data = f.read()
    return data

def writer(file, data):
    with open(file, 'w') as f:
        f.write(str(data))

class MemDir(dict):
    def __init__(self, name):
        super().__init__()
        self.parent = None
        self.name = name
        self.files = []

    def get_path(self):
        path = self.name
        parent = self.parent
        while parent is not None:
            path = parent.name + '/' + path
            parent = parent.parent
        return path

    def create_child(self, newdir):
        if type(newdir) == str:
            newdir = MemDir(name=newdir)
            newdir.parent = self
        super().__setitem__(newdir.name, newdir)

    def add_obj(self, obj):
        self.files.append(obj)

    def add_objs(self, objs):
        self.files.extend(objs)

    def traverse(self):
        yield self
        for dir in self.values():
            yield from dir.traverse()

    @staticmethod
    def __split_first_rest__(string):
        div = string.find('/')
        if div != -1:
            first, rest = string[:div], string[div + 1:]
            return first, rest
        else:
            return string, None

    def __getitem__(self, item):
        if type(item) == int:
            return self.files[item]
        elif type(item) == str:
            first, rest = self.__split_first_rest__(item)
            if rest is None:
                return super().__getitem__(item)
            else:
                return super().__getitem__(first)[rest]

    def make_subdirs(self, path):
        first, rest = self.__split_first_rest__(path)
        if first not in self:
            self.create_child(first)
        child = self[first]
        if rest is not None:
            child.make_subdirs(rest)

    def __setitem__(self, key, value):
        raise TypeError('Cannot set values in a MemDir.')
        # self.make_subdirs(key)
        # self[key].add_obj(value)

    def rename(self, newname):
        if self.parent is None:
            self.name = newname
        else:
            parent = self.parent
            pop = parent.pop(self.name)
            pop.name = newname
            parent.create_child(pop)

    def copy(self, newname=None):
        files = []
        for file in self.files:
            try:
                files.append(file.copy())
            except AttributeError:
                files.append(file)
        newdir = MemDir(newname if newname else self.name)
        newdir.files = files
        for dir in self.values():
            newdir.create_child(dir.copy())
        return newdir

    def numfiles(self):
        return len(self.files)

    def numdirs(self):
        return len(self)

    def __repr__(self):
        return f"MemDir('{self.get_path()}', D={self.numdirs()}, F={self.numfiles()})"

def load_path(path):
    tree = MemDir('.')
    for root, dirs, files in os.walk(path):
        root = root.replace('\\', '/')
        tree.make_subdirs(root)
        for file in files:
            data = loader(os.path.join(root, file))
            tree[root].add_obj([file, data])
    root = tree[path]
    root.parent = None
    del tree
    return root

def dump_tree(root, memdir):
    oldname = memdir.name
    memdir.name = root
    for dir in memdir.traverse():
        dirpath = dir.get_path()
        os.makedirs(dirpath)
        for file in dir.files:
            writer(os.path.join(dirpath, file[0]), file[1])
    memdir.name = oldname

def dump_data(root, memdir):
    oldname = memdir.name
    memdir.name = root
    for dir in memdir.traverse():
        dirpath = dir.get_path()
        os.makedirs(dirpath, exist_ok=True)
        for idx, file in enumerate(dir.files):
            writer(os.path.join(dirpath, str(idx)+EXTN), file)
    memdir.name = oldname

if __name__ == '__main1__':
    memdir = load_path('D:/MusicLab/memdir/test1 - Copy')
    dump_tree(os.path.join('D:/dumptree1/copy'), memdir)

if __name__ == '__main__':
    memdir = MemDir('.')
    # memdir.make_subdirs('child1')
    # memdir.make_subdirs('child2')
    memdir.make_subdirs('child1/child11')
    memdir.make_subdirs('child2/child22/deep/deeper')
    memdir.make_subdirs('child2/child22/deep1/deeper')
    memdir.make_subdirs('child2/child22/deep2')
    memdir['child1'].add_obj([1,2,3,4])
    # memdir['child1'] = 3
    memdir['child2/child22'].rename('CHILD22')
    memdir['child1/child11'].add_obj('a string')
    memdir['child1/child11'].add_obj(['a', 'list', 'of', (1, 2, 3)])
    child = memdir['child1/child11']
    memdir['child1'].add_objs([1, 2, 3, 4])
    memdir.rename('root')
    for dir in memdir.traverse():
        if dir.files:
            print(dir, dir.files)
        else:
            print(dir)
    dump_data('cliplib', memdir)
