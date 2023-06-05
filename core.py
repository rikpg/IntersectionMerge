#
# Module with all the merging functions
#
# Evey function with a name ending with '_merge' will be auto loaded


import networkx
import heapq
from itertools import chain
from collections import deque


def rik_merge(lsts):
    """Rik. Poggi"""
    sets = (set(e) for e in lsts if e)
    results = [next(sets)]
    for e_set in sets:
        to_update = []
        for i,res in enumerate(results):
            if not e_set.isdisjoint(res):
                to_update.insert(0,i)

        if not to_update:
            results.append(e_set)
        else:
            last = results[to_update.pop(-1)]
            for i in to_update:
                last |= results[i]
                del results[i]
            last |= e_set

    return results


def sve_merge(lsts):
    """Sven Marnach"""
    sets = {}
    for lst in lsts:
        s = set(lst)
        t = set()
        for x in s:
            if x in sets:
                t.update(sets[x])
            else:
                sets[x] = s
        for y in t:
            sets[y] = s
        s.update(t)
    ids = set()
    result = []
    for s in sets.values():
        if id(s) not in ids:
            ids.add(id(s))
            result.append(s)
    return result


def hoc_merge(lsts):    # modified a bit to make it return sets
    """hochl"""
    s = [set(lst) for lst in lsts if lst]
    i,n = 0,len(s)
    while i < n-1:
        for j in range(i+1, n):
            if s[i].intersection(s[j]):
                s[i].update(s[j])
                del s[j]
                n -= 1
                break
        else:
            i += 1
    return [set(i) for i in s]


def nik_merge(lsts):
    """Niklas B."""
    sets = [set(lst) for lst in lsts if lst]
    merged = 1
    while merged:
        merged = 0
        results = []
        while sets:
            common, rest = sets[0], sets[1:]
            sets = []
            for x in rest:
                if x.isdisjoint(common):
                    sets.append(x)
                else:
                    merged = 1
                    common |= x
            results.append(common)
        sets = results
    return sets


def pairs(lst):
    i = iter(lst)
    first = prev = item = next(i)
    for item in i:
        yield prev, item
        prev = item
    yield item, first


def kat_merge(lsts):
    """katrielalex"""
    g = networkx.Graph()
    for sub_list in lsts:
        if not sub_list:
            continue
        for edge in pairs(sub_list):
            g.add_edge(*edge)

    return networkx.connected_components(g)


def rob_merge(lsts):
    """robert king"""
    lsts = [sorted(l) for l in lsts]   # I changed this line
    one_list = heapq.merge(*[zip(l,[i]*len(l)) for i,l in enumerate(lsts)])
    previous = next(one_list)

    d = {i:i for i in range(len(lsts))}
    for current in one_list:
        if current[0]==previous[0]:
            d[current[1]] = d[previous[1]]
        previous=current

    groups=[[] for i in range(len(lsts))]
    for k in d:
        groups[d[k]].append(lsts[k])

    return [set(chain(*g)) for g in groups if g]


def agf_merge(lsts):
    """agf"""
    newsets, sets = [set(lst) for lst in lsts if lst], []
    while len(sets) != len(newsets):
        sets, newsets = newsets, []
        for aset in sets:
            for eachset in newsets:
                if not aset.isdisjoint(eachset):
                    eachset.update(aset)
                    break
            else:
                newsets.append(aset)
    return newsets


def agf_opt_merge(lists):
    """agf (optimized)"""
    sets = deque(set(lst) for lst in lists if lst)
    results = []
    disjoint = 0
    current = sets.pop()
    while True:
        merged = False
        newsets = deque()
        for _ in range(disjoint, len(sets)):
            this = sets.pop()
            if not current.isdisjoint(this):
                current.update(this)
                merged = True
                disjoint = 0
            else:
                newsets.append(this)
                disjoint += 1
        if sets:
            newsets.extendleft(sets)
        if not merged:
            results.append(current)
            try:
                current = newsets.pop()
            except IndexError:
                break
            disjoint = 0
        sets = newsets
    return results


def ste_merge(lsts):
    """steabert"""
    # this is an index list that stores the joined id for each list
    joined = range(len(lsts))
    # create an ordered list with indices
    indexed_list = sorted((el,index) for index,lst in enumerate(lsts) for el in lst)
    # loop throught the ordered list, and if two elements are the same and
    # the lists are not yet joined, alter the list with joined id
    el_0,idx_0 = None,None
    for el,idx in indexed_list:
        if el == el_0 and joined[idx] != joined[idx_0]:
            old = joined[idx]
            rep = joined[idx_0]
            joined = [rep if id == old else id for id in joined]
        el_0, idx_0 = el, idx
    return joined


def che_merge(lsts):
    """ChessMaster"""
    results, sets = [], [set(lst) for lst in lsts if lst]
    upd, isd, pop = set.update, set.isdisjoint, sets.pop
    while sets:
        if not [upd(sets[0],pop(i)) for i in range(len(sets)-1,0,-1) if not isd(sets[0],sets[i])]:
            results.append(pop(0))
    return results


def locatebin(bins, n):
    """Find the bin where list n has ended up: Follow bin references until
    we find a bin that has not moved.
    """
    while bins[n] != n:
        n = bins[n]
    return n


def ale_merge(data):
    """alexis"""
    bins = list(range(len(data)))  # Initialize each bin[n] == n
    nums = dict()

    data = [set(m) for m in data]  # Convert to sets
    for r, row in enumerate(data):
        for num in row:
            if num not in nums:
                # New number: tag it with a pointer to this row's bin
                nums[num] = r
                continue
            else:
                dest = locatebin(bins, nums[num])
                if dest == r:
                    continue # already in the same bin

                if dest > r:
                    dest, r = r, dest   # always merge into the smallest bin

                data[dest].update(data[r])
                data[r] = None
                # Update our indices to reflect the move
                bins[r] = dest
                r = dest

    # Filter out the empty bins
    have = [ m for m in data if m ]
    #print len(have), "groups in result"  #removed this line
    return have


def nik_rew_merge(lsts):
    """Nik's rewrite"""
    sets = list(map(set,lsts))
    results = []
    while sets:
        first, rest = sets[0], sets[1:]
        merged = False
        sets = []
        for s in rest:
            if s and s.isdisjoint(first):
                sets.append(s)
            else:
                first |= s
                merged = True
        if merged:
            sets.append(first)
        else:
            results.append(first)
    return results
