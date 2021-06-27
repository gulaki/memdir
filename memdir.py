import os

path = os.path.dirname(__file__)

def loader(file):
    with open(file, 'r') as f:
        data = f.read()
    return data

def writer(file, data):
    with open(file, 'w') as f:
        f.write(str(data))

class MemDir:
    def __init__(self, name):
        self.parent = None
        self.name = name
        self.dirs = {}
        self.files = []

    def get_path(self):
        path = self.name
        parent = self.parent
        while parent is not None:
            path = parent.name + '/' + path
            parent = parent.parent
        return path

    def add_dir(self, name):
        if type(name) == str:
            newdir = MemDir(name)
            newdir.parent = self
        self.dirs[newdir.name] = newdir

    def add_obj(self, obj):
        self.files.append(obj)

    def add_objs(self, objs):
        self.files.extend(objs)

    def traverse(self):
        yield self
        for dir in self.dirs.values():
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
                return self.dirs[item]
            else:
                return self.dirs[first][rest]

    def make_dir_tree(self, path):
        first, rest = self.__split_first_rest__(path)
        if first not in self.dirs:
            self.add_dir(first)
        child = self[first]
        if rest is not None:
            child.make_dir_tree(rest)

    def numfiles(self):
        return len(self.files)

    def numdirs(self):
        return len(self.dirs)

    def __repr__(self):
        return f"MemDir({self.get_path()}, D={self.numdirs()}, F={self.numfiles()})"

def load_path(path):
    tree = MemDir('.')
    for root, dirs, files in os.walk(path):
        root = root.replace('\\', '/')
        tree.make_dir_tree(root)
        for file in files:
            data = loader(os.path.join(root, file))
            tree[root].add_obj([file, data])
    return tree[path]

if __name__ == '__main__':
    memdir = load_path('test1')
    print(memdir)

if __name__ == '__main1__':
    memdir = MemDir('root')
    memdir.add_dir('child1')
    memdir.add_dir('child2')
    memdir.dirs['child1'].add_obj([1,2,3,4])
    memdir['child1'].add_dir('child11')
    memdir['child1']['child11'].add_obj('a string')
    child = memdir['child1/child11']
    # print(child[0])
    # print(child.get_path())
    # print(child)
    for dir in memdir['child1'].traverse():
        print(dir)

