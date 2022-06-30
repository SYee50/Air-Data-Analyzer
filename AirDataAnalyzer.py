""" This program summarizes and presents air quality data. """

from enum import Enum

import csv


class EmptyDatasetError(Exception):
    """ Error raised when a method requires a non-empty dataset,
    but the dataset is empty.
    """
    pass


class NoMatchingItems(Exception):
    """ Error raised when there is no data at the requested row and
    column.
    """
    pass


filename = './air_data.csv'

menu_options = {
    1: "Print Average Particulate Concentration by Zip Code and Time",
    2: "Print Minimum Particulate Concentration by Zip Code and Time",
    3: "Print Maximum Particulate Concentration by Zip Code and Time",
    4: "Print Min/Avg/Max by Zip Code",
    5: "Print Min/Avg/Max by Time",
    6: "Adjust Zip Code Filters",
    7: "Adjust Time Filters",
    8: "Load Data",
    9: "Quit"
}


class DataSet:
    """ The DataSet class will present summary tables based on
    information imported from a .csv file.
    """

    class Categories(Enum):
        """ Used to indicate which data column is of interest. """
        ZIP_CODE = 0
        TIME_OF_DAY = 1

    class Stats(Enum):
        """ Used to indicate which statistic is requested. """
        MIN = 0
        AVG = 1
        MAX = 2

    def __init__(self, header=""):
        self._labels = {DataSet.Categories.ZIP_CODE: dict(),
                        DataSet.Categories.TIME_OF_DAY: dict()}
        self._data = None
        self.header = header

    @property
    def header(self):
        """ Return the value of the _header property. """
        return self._header

    @header.setter
    def header(self, new_header: str):
        """ Set value of the _header property. """
        if not isinstance(new_header, str):
            raise TypeError
        elif len(new_header) > 30:
            raise ValueError
        else:
            self._header = new_header

    def _initialize_labels(self):
        """ Raise EmptyDatasetError when no data set is loaded.
        Populate self._labels dictionary with labels from self._data
        and True value.
        """
        if not self._data:
            raise EmptyDatasetError
        for category in self.Categories:
            self._labels[category] = \
                {i[category.value]: True for i in self._data}

    def load_file(self):
        """ Load the data from the Purple Air data file into self._data
        and return number of lines in data.
        """
        with open(filename, 'r', newline='') as air_file:
            csvreader = csv.reader(air_file)
            next(csvreader)
            self._data = [(row[1], row[4], float(row[5])) for row in csvreader]
            count = len(self._data)
        self._initialize_labels()
        print(f"{count} lines loaded")

    def get_labels(self, category: Categories):
        """ Return a list of all the keys in _labels[category]. """
        if not self._data:
            raise EmptyDatasetError
        return [key for key in self._labels[category]]

    def get_active_labels(self, category: Categories):
        """ Return a list of keys in _labels[category] that have
        True as a value.
        """
        if not self._data:
            raise EmptyDatasetError
        return [key for key, value in self._labels[category].items()
                if value is True]

    def toggle_active_label(self, category: Categories, descriptor: str):
        """ Raise KeyError if descriptor is not a key in the nested
        dictionary. Change the value of the entry associated with
        descriptor from True to False or from False to True.
        """
        if not self._data:
            raise EmptyDatasetError
        if descriptor not in self._labels[category]:
            raise KeyError
        else:
            self._labels[category][descriptor] = \
                not self._labels[category][descriptor]

    def _cross_table_statistics(self, descriptor_one: str,
                                descriptor_two: str):
        """ Raise exceptions when there is no data or list is empty.
        Create list using two parameters and loaded data.
        Calculate the average of the list.

        Args:
            descriptor_one (str): zip code of air concentration
            descriptor_two (str): time of day of air concentration
        Returns:
            tuple: min, average, max from the matching row
        """
        if not self._data:
            raise EmptyDatasetError
        concentration_list = [item[2] for item in self._data if
                              item[0] == descriptor_one and
                              item[1] == descriptor_two]
        if not concentration_list:
            raise NoMatchingItems
        else:
            average = sum(concentration_list) / len(concentration_list)
            return min(concentration_list), average, max(concentration_list)

    def display_cross_table(self, stat: Stats):
        """ Displays a cross table of different air concentration
        statistics.
        """
        if not self._data:
            raise EmptyDatasetError
        print()
        print(f"{'':<7}", end="")
        for i in self.get_active_labels(DataSet.Categories.TIME_OF_DAY):
            print(f"{i:>8}", end="")
        print()
        for j in self.get_active_labels(DataSet.Categories.ZIP_CODE):
            print(f"{j:<7}", end="")
            for k in self.get_active_labels(DataSet.Categories.TIME_OF_DAY):
                try:
                    statistics = self._cross_table_statistics(j, k)
                    print(f"{statistics[stat.value]:>8.2f}", end="")
                except NoMatchingItems:
                    print(f"{'N/A':>8}", end="")
            print()

    def _table_statistics(self, row_category: Categories, label: str):
        """ Given a category and a label, calculate summary statistics
        for the rows that match that label. Include only rows that the
        category has active labels.

        Args:
            row_category (Categories): category from Categories(Enum)
            label (str): zip code or time of day

        Returns:
            tuple: min, average, max from matching row
        """
        if row_category.value == 0:
            alternate_category = DataSet.Categories.TIME_OF_DAY
        else:
            alternate_category = DataSet.Categories.ZIP_CODE
        active_labels = self.get_active_labels(alternate_category)
        if not self._data:
            raise EmptyDatasetError
        concentration_list = [item[2] for item in self._data
                              if item[row_category.value] == label and
                              item[alternate_category.value] in active_labels]
        if not concentration_list:
            raise NoMatchingItems
        else:
            average = sum(concentration_list) / len(concentration_list)
            return min(concentration_list), average, max(concentration_list)

    def display_field_table(self, rows: Categories):
        """ Given a category, display one row for each label in that
        category with min, avg, max displayed for each row. Include
        only rows where the other_category's label is active.
        """
        if not self._data:
            raise EmptyDatasetError
        print()
        print("The following data are from sensors matching these criteria:")
        print()
        if rows.value == 0:
            other_category = DataSet.Categories.TIME_OF_DAY
        else:
            other_category = DataSet.Categories.ZIP_CODE
        for label in self.get_active_labels(other_category):
            print(f"- {label}")
        print(f"{'':8}{'Minimum':8}{'Average':8}{'Maximum':8}")
        for item in self.get_active_labels(rows):
            print(f"{item:7}", end="")
            try:
                for statistic in self._table_statistics(rows, item):
                    print(f"{statistic:8.2f}", end="")
            except NoMatchingItems:
                print(f"{'N/A':>8}{'N/A':>8}{'N/A':>8}", end="")
            print()


def print_menu():
    """ Print the menu of choices. """
    print("Main Menu")
    for key in menu_options:
        print(f"{key}: {menu_options[key]}")


def menu(my_dataset: DataSet):
    """ Print the main menu, and obtain the user's menu choice.
    Convert the user's input into an integer, and handle an exception
    for a non-numeric input. Exit menu loop with integer 9. Print
    the user's menu choice. Execute the user's menu choice.
    """
    while True:
        print()
        print(my_dataset.header)
        print_menu()
        try:
            user_choice = int(input("Please choose a number from the menu: "))
        except ValueError:
            print("Please enter a number.")
            continue
        if user_choice == 9:
            print("Goodbye! Thank you for looking at the menu.")
            break
        elif user_choice == 1:
            try:
                my_dataset.display_cross_table(DataSet.Stats.AVG)
            except EmptyDatasetError:
                print("Please load a dataset first.")
        elif user_choice == 2:
            try:
                my_dataset.display_cross_table(DataSet.Stats.MIN)
            except EmptyDatasetError:
                print("Please load a dataset first.")
        elif user_choice == 3:
            try:
                my_dataset.display_cross_table(DataSet.Stats.MAX)
            except EmptyDatasetError:
                print("Please load a dataset first.")
        elif user_choice == 4:
            try:
                my_dataset.display_field_table(DataSet.Categories.ZIP_CODE)
            except EmptyDatasetError:
                print("Please load a dataset first.")
        elif user_choice == 5:
            try:
                my_dataset.display_field_table(
                    DataSet.Categories.TIME_OF_DAY)
            except EmptyDatasetError:
                print("Please load a dataset first.")
        elif user_choice == 6:
            manage_filters(my_dataset, DataSet.Categories.ZIP_CODE)
        elif user_choice == 7:
            manage_filters(my_dataset, DataSet.Categories.TIME_OF_DAY)
        elif user_choice == 8:
            my_dataset.load_file()
        else:
            print("Sorry, your choice is not on the menu.")


def manage_filters(dataset: DataSet, category: DataSet.Categories):
    """ Print menu-like list of all labels and values for a given
    category. Ask user for choice of which label to switch between
    active or inactive.
    Note: dataset.get_active_labels() may raise EmptyDatasetError
    """
    try:
        labels = {i: label for i, label in
                  enumerate(dataset.get_labels(category), 1)}
    except EmptyDatasetError:
        print("Please load a dataset first.")
        return
    while True:
        active = dataset.get_active_labels(category)
        print("The following labels are in the dataset:")
        for item, label in labels.items():
            print(f"{item}: {label:<10} "
                  f"{'ACTIVE' if label in active else 'INACTIVE'}")
        selection = input("Please select an item to toggle or enter a "
                          "blank line when you are finished.")
        if selection == "":
            break
        try:
            int_selection = int(selection)
        except ValueError:
            print("Please enter a number or a blank line.")
            continue
        if int_selection in labels:
            dataset.toggle_active_label(category, labels[int_selection])
        else:
            print("Please enter a number from the list.")


def main():
    """ Obtain the user's name, and return a polite greeting. Print the
    toppings' menu, and handle the user's input. Create DataSet
    instance. Ask user for valid header.
    """
    username = input("Hello, please enter your name: ")
    print("Welcome, " + username + ", to the Air Quality database.")
    while True:
        header = input("Please enter a header: ")
        try:
            purple_air = DataSet(header)
            break
        except TypeError:
            print("Please enter a string only.")
        except ValueError:
            print("Please enter a string of 30 characters or less.")
    menu(purple_air)


if __name__ == "__main__":
    main()
