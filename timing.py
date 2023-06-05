import argparse
import core
import json
from pathlib import Path
import random
from statistics import mean
import sys
import time
import timeit


# =================
# Benchmark classes
# =================

class Benchmark:
    def __init__(self):
        self.lsts = []
        self.info = ''
        self.setup = 'lists = [[item for item in lst] for lst in lsts]'
        self.load()
        self.build_info()

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
        self.info = f'{num} lists, average size {size // num}, max size {max}'


class Niklas(Benchmark):
    def __init__(self, filename):
        self.filename = filename
        super().__init__()

    def load(self):
        self.lsts = [
            [int(x) for x in line.split()]
            for line in Path(self.filename).read_text().splitlines()
        ]

    def build_info(self):
        super().build_info()
        self.info += f'\n(from file: {self.filename})'


class Sven(Benchmark):
    def load(self):
        self.lsts = json.loads(Path('./lists/sven_list.txt').read_text())


class Agf(Benchmark):
    def load(self):
        self.lsts = [
            random.sample(range(10000), random.randint(0, 500))
            for _ in range(2000)
        ]


# ======================================
# Function for building Nik's test lists
# ======================================

def build_timing_list(
    filename,
    class_count=50,
    class_size=1000,
    list_count_per_class=10,
    large_list_sizes=(100, 1000),
    small_list_sizes=(0, 100),
    large_list_probability=0.5
):
    large_list_sizes = list(range(*large_list_sizes))
    small_list_sizes = list(range(*small_list_sizes))
    with open(filename, "w") as f:
        lists = []
        classes = [
            list(range(class_size * i, class_size * (i + 1)))
            for i in range(class_count)
        ]
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


def build_all_timing_lists():
    print('building test list (for Nik test) ... ', end='')
    sys.stdout.flush()
    param = dict(class_count=50,
                 class_size=1000,
                 list_count_per_class=100,
                 large_list_sizes=(100, 1000),
                 small_list_sizes=(0, 100),
                 large_list_probability=0.5,
                 filename='./lists/timing_1.txt')
    build_timing_list(**param)

    param = dict(class_count=15,
                 class_size=1000,
                 list_count_per_class=300,
                 large_list_sizes=(100, 1000),
                 small_list_sizes=(0, 100),
                 large_list_probability=0.5,
                 filename='./lists/timing_2.txt')
    build_timing_list(**param)

    param = dict(class_count=15,
                 class_size=1000,
                 list_count_per_class=300,
                 large_list_sizes=(100, 1000),
                 small_list_sizes=(0, 100),
                 large_list_probability=0.1,
                 filename='./lists/timing_3.txt')
    build_timing_list(**param)
    print('done')


# ===============
# Timing function
# ===============

def timing(bench, number):
    print('\nTiming with: >> {} << Benchmark'.format(bench.__class__.__name__))
    print('Info: {}'.format(bench.info))

    print('-- Press Ctrl-C to skip a test --\n')

    times = []
    for name, value in vars(core).items():
        if name.endswith('_merge'):
            print('timing: {} '.format(value.__doc__), end='')
            sys.stdout.flush()
            try:
                # We pass number to repeat and leave number to 1.
                # This ensures the setup is repeated before every
                # iteration. We put `bench.lsts` into the execution
                # namespace. The setup does the deepcopy into `lists`
                # (and this deepcopy doesn't count in timings). The
                # benched execution uses the deepcopied list. This way,
                # if any function has side effects, they don't impact
                # other runs.
                t = mean(timeit.repeat(
                    f'{name}(lists)',
                    setup=bench.setup,
                    number=1,
                    repeat=number,
                    globals={'lsts': bench.lsts, **core.__dict__}
                ))
            except KeyboardInterrupt:
                print(' skipped.')
                try:
                    time.sleep(0.2)
                except KeyboardInterrupt:
                    print('Two fast Ctrl-C - exiting')
                    sys.exit(0)

            else:
                times.append((t, value.__doc__))
                print(' --   {:0.4f}   -- '.format(t))

    print('\nTiming Results:')
    times = sorted(times)
    best_t, best_name = times[0]
    for t, name in times:
        factor = t / best_t
        fmt = '.2g' if factor < 99 else '.0f'
        print(f'{t:0.3f} ({factor:{fmt}}x) -- {name}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Timing merge solutions.')
    list_file = parser.add_mutually_exclusive_group()
    list_file.add_argument('--new', action='store_true',
                           help='build a new test list')
    args = parser.parse_args()

    if args.new:
        build_all_timing_lists()

    timing(Niklas('./lists/timing_1.txt'), number=3)
    timing(Niklas('./lists/timing_2.txt'), number=3)
    timing(Niklas('./lists/timing_3.txt'), number=3)
    timing(Sven(), number=500)
    timing(Agf(), number=10)
