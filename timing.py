import core
import timeit
import random
import sys
import argparse
import time


# =================
# Benchmark classes
# =================

class Benchmark:

    def __init__(self):
        with open('core.py') as f:
            self.setup = f.read()

        self.setup += """\nfrom copy import deepcopy\n"""

        self.load()
        self.build_info()
        self.extend_setup()

    def load(self):
        raise NotImplementedError

    def build_info(self):
        size = 0
        num = 0
        max = 0
        for lst in self.lsts:
            size += len(lst)
            if len(lst) > max:
                max = len(lst)
            num += 1
        self.info = "{} lists, average size {}, max size {}".format(num, size//num, max)

    def extend_setup(self):
        self.setup += ''
        raise NotImplementedError


class Niklas(Benchmark):

    def __init__(self, filename):
        self.filename = filename
        super().__init__()

    def load(self):
        self.lsts = []
        with open(self.filename, "r") as f:
            for line in f:
                lst = [int(x) for x in line.split()]
                self.lsts.append(lst)

    def build_info(self):
        super().build_info()
        self.info += '\n(from file: {})'.format(self.filename)

    def extend_setup(self):
        self.setup += """

lsts = []
size = 0
num = 0
max = 0
for line in open("{0}", "r"):
  lst = [int(x) for x in line.split()]
  size += len(lst)
  if len(lst) > max: max = len(lst)
  num += 1
  lsts.append(lst)
""".format(self.filename)


class Sven(Benchmark):

    def load(self):
        import json
        with open('./lists/sven_list.txt') as f:
            self.lsts = json.loads(f.read())

    def extend_setup(self):
        self.setup += """
import json
with open('./lists/sven_list.txt') as f:
    lsts = json.loads(f.read())
"""


class Agf(Benchmark):

    def load(self):
        import random
        tenk = range(10000)
        self.lsts = [random.sample(tenk, random.randint(0, 500)) for _ in range(2000)]

    def extend_setup(self):
        self.setup += """\nlsts = {}""".format(repr(self.lsts))


# ======================================
# Function for building Nik's test lists
# ======================================

def build_timing_list(filename,
                      class_count=50,
                      class_size=1000,  
                      list_count_per_class=10,
                      large_list_sizes = (100, 1000),
                      small_list_sizes = (0, 100),
                      large_list_probability = 0.5):

  large_list_sizes = list(range(*large_list_sizes))
  small_list_sizes = list(range(*small_list_sizes))
  with open(filename, "w") as f:
    lists = []
    classes = [list(range(class_size*i, class_size*(i+1))) for i in range(class_count)]
    for c in classes:
      # distribute each class across ~300 lists
      for i in range(list_count_per_class):
        lst = []
        if random.random() < large_list_probability:
          size = random.choice(large_list_sizes)
        else:
          size = random.choice(small_list_sizes)
        nums = set(c)
        for j in range(size):
          x = random.choice(list(nums))
          lst.append(x)
          nums.remove(x)
        random.shuffle(lst)
        lists.append(lst)
    random.shuffle(lists)
    for lst in lists:
      f.write(" ".join(str(x) for x in lst) + "\n")


# ===============
# Timing function
# ===============

def timing(bench, number):
    print('\nTiming with: >> {} << Benchmark'.format(bench.__class__.__name__))
    print('Info: {}'.format(bench.info))
    setup = bench.setup
    
    print('-- Press Ctrl-C to skip a test --\n')

    times = []
    for name, value in vars(core).items():
        if name.endswith('_merge'):
            print('timing: {} '.format(value.__doc__), end='')
            sys.stdout.flush()
            try:
                t = timeit.timeit("{}(deepcopy(lsts))".format(name),
                                  setup=setup,
                                  number=number)
            except KeyboardInterrupt:
                print(' skipped.')
                try:
                    time.sleep(0.2)
                except KeyboardInterrupt:
                    print('Two fast Ctrl-C - exiting')
                    sys.exit(0)
                
            else:
                times.append((value.__doc__, t))
                print(' --   {:0.4f}   -- '.format(t))

    print('\nTiming Results:')
    for name,t in sorted(times, key=operator.itemgetter(1)):
        print('{:0.3f}  -- {}'.format(t,name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Timing merge solutions.')
    list_file = parser.add_mutually_exclusive_group()
    list_file.add_argument('--new', action='store_true',
                           help='build a new test list')
    args = parser.parse_args()

    if args.new:
        print('building test list (for Nik test) ... ', end='')
        sys.stdout.flush()
        param = dict(class_count = 50,
                     class_size = 1000,
                     list_count_per_class = 100,
                     large_list_sizes = (100, 1000),
                     small_list_sizes = (0, 100),
                     large_list_probability = 0.5,
                     filename = './lists/timing_1.txt')
        build_timing_list(**param)

        param = dict(class_count = 15,
                     class_size = 1000,
                     list_count_per_class = 300,
                     large_list_sizes = (100, 1000),
                     small_list_sizes = (0, 100),
                     large_list_probability = 0.5,
                     filename = './lists/timing_2.txt')
        build_timing_list(**param)
        
        param = dict(class_count = 15,
                     class_size = 1000,
                     list_count_per_class = 300,
                     large_list_sizes = (100, 1000),
                     small_list_sizes = (0, 100),
                     large_list_probability = 0.1,
                     filename = './lists/timing_3.txt')
        build_timing_list(**param)
        print('done')
        
    timing(Niklas('./lists/timing_1.txt'), number=3)
    timing(Niklas('./lists/timing_2.txt'), number=3)
    timing(Niklas('./lists/timing_3.txt'), number=3)
    timing(Sven(), number=500)
    timing(Agf(), number=10)
