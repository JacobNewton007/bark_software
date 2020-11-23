import os
from collections import OrderedDict

import bark_commands


class Option:
    def __init__(self, name, command, prep_call=None):
        self.name = name 
        self.command = command
        self.prep_call = prep_call

    def choose(self):
        data = self.prep_call() if self.prep_call else None # callS The preparation step if specified
        message = self.command.execute(data) if data else self.command.execute() #execute the command, passing in the data from the preparation, if any
        print(message)

    def __str__(self):
        return self.name #Represents the option as its name instead of the default python behavior


def clear_screen():
    clear = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear)


def print_options(options):
    for shortcut, option in options.items():
        print(f'({shortcut}) {option}')
    print()


def option_choice_is_valid(choice, options):
    return choice in options or choice.upper() in options # the choice is valid if the letter matches one of the keys in the options dictionary.

def get_option_choice(options):
    choice = input('Choose an option: ')
    while not option_choice_is_valid(choice, options):
        print('Invalid choice')
        choice = input('Choose an option: ')
    return options[choice.upper()]

def get_user_input(label, required=True):
    value = input(f'{label}: ') or None
    while required and not value:
        value = input(f'{label}: ') or None
    return value

def get_new_bookmark_data():# function to get necessary data for adding a new bookmark
    return {
        'title': get_user_input('Title'),
        'url': get_user_input('URL'),
        'note': get_user_input('Note', required=False),
    }

def get_bookmark_id_for_deletion():
    return get_user_input('Enter a bookmark ID to delete')

def get_new_bookmark_info():
    bookmark_id = get_user_input('Enter a bookmark ID to edit')
    field = get_user_input('Choose a value to edit (title, URL, notes)')
    new_value = get_user_input(f'Enter the new value for {field}')
    return {
        'id': bookmark_id,
        'update': {field: new_value},
    }



def get_github_import_options():
    return {
        'github_username': get_user_input('GitHub username'),
        'preserve_timestamps':
            get_user_input(
                'preserve timestamps [Y/n]',
                required=False
            ) in {'Y', 'y', None},
    }


def loop():
    clear_screen()

    options = OrderedDict({
        'A': Option('Add a bookmark', bark_commands.AddBookmarkCommand(), prep_call=get_new_bookmark_data),
        'B': Option('List bookmarks by date', bark_commands.ListBookmarkCommand()),
        'T': Option('List bookmarks by title', bark_commands.ListBookmarkCommand(order_by='title')),
        'D': Option('Delete a bookmark', bark_commands.DeleteBookmarkCommand(), prep_call=get_bookmark_id_for_deletion),
        'Q': Option('Quit', bark_commands.QuitCommad()),
        'G': Option('Import Github stars', bark_commands.ImportGitHubStarCommand(), prep_call=get_github_import_options),
        'E': Option('Edit bookmarks', bark_commands.EditBookmarkCommand(), prep_call=get_new_bookmark_info),
    })
    print_options(options)
    chosen_option = get_option_choice(options)
    chosen_option.choose()
    
    _ = input('Press Enter to run menu')

if __name__ == '__main__':
    bark_commands.CreateBookmarkTableCommand().execute()

    while True:
        loop() # loops forever (until the user chooses the option corresponding to QuitCommand)