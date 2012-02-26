import core
import timeit
import random
import sys
import operator
import argparse
import os
import re

parser = argparse.ArgumentParser(description='Timing merge solutions.')
list_file = parser.add_mutually_exclusive_group()
list_file.add_argument('--new', action='store_true',
                       help='build a new test list for Niklas timing test')
list_file.add_argument('-f', '--filename',
                       help='use this file for Niklas timing test')

args = parser.parse_args()

# (this part is ugly I know)
if args.filename is not None:
    FILENAME = args.filename    # if args.new FILENAME will be modified
else:
    filename = './lists/nik_test0.txt'
    files = os.listdir('./lists')
    for f in sorted(files):
        if f.startswith('nik_test'):
            filename = os.path.join('./lists/', f)
    FILENAME = filename

if args.new:
  print('building test list (for Nik test) ... ', end='')
  sys.stdout.flush()
  FILENAME = re.sub(r'\d', lambda x: str(int(x.group()) + 1) , FILENAME)

  with open(FILENAME, 'w') as f:

    lists = []
    classes = [range(1000*i, 1000*(i+1)) for i in range(15)]
    for c in classes:
      # distribute each class across ~300 lists
      for i in range(300):
        lst = []
        if random.random() > 0.9:
          size = random.randint(100, 1000);
        else:
          size = random.randint(0, 50);
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

  print('done')


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

    def load(self):
        self.lsts = []
        with open(FILENAME, "r") as f:
            for line in f:
                lst = [int(x) for x in line.split()]
                self.lsts.append(lst)

    def build_info(self):
        super().build_info()
        self.info += '\n(from file: {}'.format(FILENAME)

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
""".format(FILENAME)

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
            else:
                times.append((value.__doc__, t))
                print(' --   {}   -- '.format(t))

    print('\nTiming Results:')
    for name,t in sorted(times, key=operator.itemgetter(1)):
        print('{}  -- {}'.format(t,name))


if __name__ == '__main__':
    timing(Niklas(), number=3)
    timing(Sven(), number=1000)
    timing(Agf(), number=10)
