import os

path = os.path.dirname(__file__)

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
        self[newdir.name] = newdir

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

    def rename(self, newname):
        if self.parent is None:
            self.name = newname
        else:
            parent = self.parent
            pop = parent.pop(self.name)
            pop.name = newname
            parent.create_child(pop)

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

if __name__ == '__main1__':
    memdir = load_path('D:/MusicLab/memdir/test1 - Copy')
    dump_tree(os.path.join('D:/dumptree1/copy'), memdir)

if __name__ == '__main__':
    memdir = MemDir('.')
    memdir.make_subdirs('child1')
    memdir.make_subdirs('child2')
    memdir['child1'].add_obj([1,2,3,4])
    memdir.make_subdirs('child1/child11')
    memdir.make_subdirs('child2/child22/deep/deeper')
    memdir.make_subdirs('child2/child22/deep1/deeper')
    memdir.make_subdirs('child2/child22/deep2')
    memdir['child2/child22'].rename('CHILD22')
    memdir['child1/child11'].add_obj('a string')
    child = memdir['child1/child11']
    for dir in memdir.traverse():
        print(dir)
