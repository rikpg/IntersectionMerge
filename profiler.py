from argparse import ArgumentParser
import cProfile
import json
from pathlib import Path
import random
import subprocess

import core
from timing import build_all_timing_lists


if __name__ == '__main__':
    parser = ArgumentParser(
        prog='Algorithm profiler',
        description='Profile any given function from "core.py", '
                    'with any dataset from "lists/".',
    )
    parser.add_argument(
        '-f', '--function', dest='function', action='store', required=True, type=str,
        help='Name of the function to profile. You can give the function\'s full name '
             '("ale_merge"), the function\'s abbreviated name ("ale") or the function\'s '
             'display name ("alexis", as found in the docstring).'
    )
    parser.add_argument(
        '-l', '--list', dest='list', action='store', required=True, type=str,
        help='Name of the list to profile with (e.g.: "timing_1" or "timing_1.txt").'
    )
    parser.add_argument(
        '-n', '--new', dest='new', action='store_true', default=False,
        help='Rebuild all "timing_*.txt" test lists.'
    )
    args = parser.parse_args()
    if args.new:
        build_all_timing_lists()

    func_name: str = args.function.strip()
    func = getattr(core, func_name, getattr(core, f'{func_name}_merge', None))
    if not func:
        for obj in core.__dict__.values():
            if func_name == getattr(obj, '__doc__', None):
                func = obj
                break
    assert callable(func), f'Object {func.__name__} is not a function.'

    list_name: str = args.list.strip()
    if not list_name.endswith('.txt'):
        list_name = f'{list_name}.txt'
    list_path = Path('.', 'lists', list_name)
    if list_name in ('sven_list.txt', 'test_list.txt'):
        lists = json.loads(list_path.read_text())
    elif list_name == 'agf_list.txt':
        lists = [
            random.sample(range(10000), random.randint(0, 500))
            for _ in range(2000)
        ]
    else:
        with open(list_path, 'r') as f:
            lists = [[int(x) for x in line.split()] for line in f]
    assert len(lists) > 0, 'It would be better if the dataset had some data.'

    prof_file_name = f'{func.__name__}_{list_name}.prof'
    cProfile.runctx('func(lists)', globals(), locals(), prof_file_name)
    try:
        subprocess.run(['snakeviz', prof_file_name])
    except KeyboardInterrupt:
        exit()
