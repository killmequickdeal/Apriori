import itertools
import sys
import math
from prettytable import PrettyTable


def main():
    file = sys.argv[1]
    min_support = float(sys.argv[2])
    min_conf = float(sys.argv[3])

    # read lines from file
    with open('./' + file) as f:
        lines = f.read().splitlines()

    # make list containing all lines as lists
    line_list = []
    for linestring in lines:
        # splitting string makes a list
        line_list.append(linestring.split())

    # find total number of data points
    total_num = len(line_list)

    # calculate min support for this data set
    min_support = int(total_num*min_support)

    # make domain
    domain = find_initial_domain(lines)  # set

    freq_size = 1
    total_freq_items = set()
    while freq_size <= len(domain):

        # find combinations given current combination size
        combs = list(itertools.combinations(domain, freq_size))

        # get freq items
        freq_items = find_freq_items(combs, line_list, min_support)

        # add to total freq items
        for item in freq_items:
            total_freq_items.add(item)

        # remake domain
        domain = set()
        for item in freq_items:
            for i in item:
                domain.add(i)

        freq_size += 1

    print("FREQUENT ITEM SETS")
    print(total_freq_items)

    freq_item_set_counts = find_closed_and_max_freq_item_sets(freq_size, total_freq_items, line_list)

    rules = find_association_rules(total_freq_items, freq_item_set_counts, line_list, total_num)

    print_rules_and_statistics(rules, min_conf)


def print_rules_and_statistics(rules: dict, min_conf: float) -> None:
    """
    output the final association rules and their corresponding statistics
    :param rules: association rules & statistics dictionary
    :param min_conf: the minimum confidence value
    :return: None
    """
    print()
    table = PrettyTable()
    table.field_names = ['Rule', 'confidence', 'lift', 'all_conf', 'cosine']
    for k, v in rules.items():
        if v['confidence'] >= min_conf:
            val = ''.join(v for v in k[0])
            implication = ''.join(v for v in k[1])
            table.add_row([val + ' -> ' + implication, v['confidence'], v['lift'], v['all_conf'], v['cosine']])

    print(table)


def count_frequencies(sets_to_find_freq_for: set, line_list: list) -> dict:
    """
    Count the frequencies for the given sets
    :param sets_to_find_freq_for: sets to find freq for
    :param line_list: list of lines from file
    :return: dict containing set : frequency pairs
    """
    counts = dict.fromkeys(sets_to_find_freq_for, 0)
    for k, v in counts.items():
        for l in line_list:
            if all(item in l for item in k):
                counts[k] += 1
    return counts


def find_association_rules(total_freq_items: set, freq_item_set_counts: dict, line_list: list, total_num: int) -> dict:
    """
    Find association rules for the given frequent item sets
    :param total_freq_items: set of all frequent item sets
    :param freq_item_set_counts: frequency counts for the frequent item sets
    :param line_list: list of all lines from file
    :param total_num: total number of lines in file
    :return: dict containing all association rules and their statistics
    """
    assoc_rule_dict = {}
    for item in total_freq_items:
        if len(item) > 1:

            # Create set of all subsets 1 < size < freq_item_set_size -1
            subsets = set(itertools.chain.from_iterable(itertools.combinations(item, n) for n in range(1, len(item))))

            for ss in subsets:
                implication = tuple(set(item).symmetric_difference(ss))

                # count frequencies so both sides of the implication
                subset_freqs = count_frequencies((ss, implication), line_list)

                confidence = freq_item_set_counts[item] / subset_freqs[ss]
                lift = confidence / (subset_freqs[implication] / total_num)
                all_conf = freq_item_set_counts[item] / max(subset_freqs[ss], subset_freqs[implication])
                cosine = freq_item_set_counts[item] / math.sqrt(subset_freqs[ss] * subset_freqs[implication])
                assoc_rule_dict[(ss, implication)] = {'confidence': confidence, 'lift': lift, 'all_conf': all_conf, 'cosine': cosine}

    return assoc_rule_dict


def superset_in_max_freq_item_set(max_freq_item_sets: set, tup: tuple) -> bool:
    """
    check if superset is already in the max frequent item sets
    :param max_freq_item_sets: the current max frequent item sets
    :param tup: the tuple to check for in the max frequent item sets
    :return: boolean of the outcome
    """
    has_superset = False
    # for all maximal frequent items
    for m in max_freq_item_sets:
        if all(item in m for item in tup):  # check if any are a superset
            has_superset = True
    return has_superset


def superset_and_same_freq_in_closed_freq_item_set(closed_freq_item_sets: set, tup: tuple, counts: dict) -> bool:
    """
    check if superset with same frequency is already in the closed frequent item sets
    :param closed_freq_item_sets: the current closed frequent item sets
    :param tup: the tuple to check for in the closed frequent item sets
    :param counts: the frequency counts for these the frequent item sets
    :return: boolean of the outcome
    """
    has_superset = False
    # for all closed frequent items
    for m in closed_freq_item_sets:
        # check if any are a superset with the same frequency
        if all(item in m for item in tup) and counts[tup] == counts[m]:
            has_superset = True

    return has_superset


def find_closed_and_max_freq_item_sets(freq_size: int, total_freq_items: set, line_list: list) -> dict:
    """
    find closed and max frequent item sets from the frequent item sets
    :param freq_size: the maximal frequent item set size
    :param total_freq_items: set of all frequent item sets
    :param line_list: list of all lines from file
    :return: dict containing all the frequent item set counts
    """
    # count number of records each frequent item set appears in
    counts = count_frequencies(total_freq_items, line_list)

    # start at max item set size
    freq_size -= 1
    closed_freq_item_sets = set()
    max_freq_item_sets = set()

    while freq_size > 0:
        # for all frequent items
        for k, v in counts.items():
            # continue if equal to current size
            if len(k) == freq_size:

                if not superset_in_max_freq_item_set(max_freq_item_sets, k):
                    max_freq_item_sets.add(k)

                if not superset_and_same_freq_in_closed_freq_item_set(closed_freq_item_sets, k, counts):
                    closed_freq_item_sets.add(k)

        freq_size -= 1

    print("MAXIMAL ITEM SETS")
    print(max_freq_item_sets)
    print("CLOSED ITEM SETS")
    print(closed_freq_item_sets)

    return counts


def find_freq_items(domain: set, line_list: list, min_support: int) -> dict:
    """
    count the number of lists each item appears in
    :param domain: the domain to find counts for
    :param line_list: all lines from the file
    :param min_support: the minimum support required to be a frequent item
    :return: list of frequent items which meet the min_support restriction
    """

    filtered_list = []
    for val in domain:
        count = 0
        for l in line_list:
            if all(item in l for item in val):
                count += 1
        if count >= min_support:
            filtered_list.append(val)

    return filtered_list


def combine_lines(lines: list) -> list:
    """
    combines all lists into one big list
    :param lines: lines from file in string form
    :return: lines from file in list form
    """
    lines_list = []
    for l in lines:
        lines_list.extend(l.split())

    return lines_list


def find_initial_domain(lines: list) -> list:
    """
    finds all present values in the data set
    :param lines: lines from file in string form
    :return: values present in the file
    """
    line_list = combine_lines(lines)
    possible_values = set(line_list)
    return possible_values


if __name__ == "__main__":
    main()
