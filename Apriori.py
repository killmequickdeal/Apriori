import itertools
import sys

def main():

    # read lines from file
    with open('./Dataset1.dat') as f:
        lines = f.read().splitlines()

    # make list containing all lines as lists
    line_list = []
    for linestring in lines:
        # splitting string makes a list
        line_list.append(linestring.split())

    # find total number of data points
    total_num = len(line_list)

    # calculate min support for this data set
    min_support = int(total_num*float(sys.argv[1]))

    # make domain
    domain = find_initial_domain(lines)  # set

    print("DOMAIN")
    print(domain)

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
        print(domain)

        freq_size += 1

    print_freq_itemsets(total_freq_items)
    # TODO: combine these functions
    find_max_freq_item_sets(freq_size, total_freq_items)

    find_closed_freq_item_sets(freq_size, total_freq_items, line_list)


def find_max_freq_item_sets(freq_size, total_freq_items):

    # start at max item set size
    freq_size -= 1
    max_freq_item_sets = set()
    while freq_size > 0:
        # for all frequent items
        for tup in total_freq_items:
            # continue if equal to current size
            if len(tup) == freq_size:
                # if no superset, add
                if not superset_in_max_freq_item_set(max_freq_item_sets, tup):
                    max_freq_item_sets.add(tup)
        freq_size -= 1
    print("MAXIMAL")

    print(max_freq_item_sets)


def superset_in_max_freq_item_set(max_freq_item_sets, tup):
    has_superset = False
    # for all maximal frequent items
    for m in max_freq_item_sets:
        if all(item in m for item in tup):  # check if any are a superset
            has_superset = True
    return has_superset


def find_closed_freq_item_sets(freq_size, total_freq_items, line_list):
    counts = dict.fromkeys(total_freq_items,0)
    for k, v in counts.items():
        for l in line_list:
            if all(item in l for item in k):
                counts[k] += 1

    # start at max item set size
    freq_size -= 1
    closed_freq_item_sets = set()
    while freq_size > 0:
        # for all frequent items
        for k, v in counts.items():
            # continue if equal to current size
            if len(k) == freq_size:
                has_superset = False
                # for all closed frequent items
                for m in closed_freq_item_sets:
                    # check if any are a superset with the same frequency
                    if all(item in m for item in k) and counts[k] == counts[m]:
                        has_superset = True
                # if no superset with same freq, add
                if not has_superset:
                    closed_freq_item_sets.add(k)
        freq_size -= 1
    print("CLOSED")
    print(closed_freq_item_sets)



def find_freq_items(domain: set, line_list: list, min_support: int) -> dict:
    """
        count the number of lists each item appears in
        :param domain:
        :param line_list:
        :param min_support:
        :return: item count
        """

    filtered_list = []
    for val in domain:
        count = 0
        for l in line_list:
            if all(item in l for item in val):
                count += 1
        if count > min_support:
            filtered_list.append(val)

    return filtered_list


def combine_lines(lines: list) -> list:
    """
    combines all lists into one big list
    :param lines:
    :return:
    """
    lines_list = []
    for l in lines:
        lines_list.extend(l.split())

    return lines_list


def find_initial_domain(lines: list) -> list:
    """
    finds all present values in the data set
    :param lines:
    :return:
    """
    line_list = combine_lines(lines)
    possible_values = set(line_list)
    return possible_values

def print_freq_itemsets(total_freq_items: set) -> None:
    # for tup in total_freq_items:
    #
    #     item_string = ""
    #     for item in tup:
    #         item_string += item + " - "
    #     print(item_string)
    print("FREQUENT")
    print(total_freq_items)

if __name__ == "__main__":
    main()
