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

    def add_dir(self, newdir):
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

    def make_dir_tree(self, path):
        first, rest = self.__split_first_rest__(path)
        if first not in self:
            self.add_dir(first)
        child = self[first]
        if rest is not None:
            child.make_dir_tree(rest)

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
        tree.make_dir_tree(root)
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

if __name__ == '__main__':
    memdir = load_path('test1')
    dump_tree(os.path.join('D:/dumptree1/copy'), memdir)

if __name__ == '__main1__':
    memdir = MemDir('.')
    memdir.add_dir('child1')
    memdir.add_dir('child2')
    memdir['child1'].add_obj([1,2,3,4])
    memdir['child1'].add_dir('child11')
    memdir['child1']['child11'].add_obj('a string')
    child = memdir['child1/child11']
    # print(child[0])
    # print(child.get_path())
    # print(child)
    for dir in memdir['child1'].traverse():
        print(dir)

