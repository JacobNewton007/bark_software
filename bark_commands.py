import sys
from datetime import datetime
from bark_databasemanager import DatabaseManager

db = DatabaseManager('bookmarks.db')# sqlite3 will automatically create this database file if it doesn't exist.

class CreateBookmarkTableCommand:#
    def execute(self):# this will eventually be called when Bark starts up 
        db.create_table('bookmarks', {# create the bookmarks table the necessary column and constraints
            'id': 'integer primary key autoincrement',
            'title': 'text not null',
            'url': 'text not null',
            'note': 'text',
            'date_added': 'text not null',
        })

class AddBookmarkCommand:
    def execute(self, data, timestamp=None):
        data['date_added'] = timestamp or datetime.utcnow().isoformat()#adds the current datetimes as the records is added
        db.add('bookmarks', data)# using the databasemanager.add method makes short work of adding a record.
        return 'Bookmarks added!'# the user will recieve this message in the presentation layer later.

class ListBookmarkCommand:
    def __init__(self, order_by='date_added'):
        self.order_by = order_by

    def execute(self):
        return db.select('bookmarks', order_by=self.order_by).fetchall()

class EditBookmarkCommand:
    def execute(self, data):
        db.update(
            'bookmarks',
            {'id': data['id']},
            data['update'],
        )
        return 'Bookmark updated!'



class DeleteBookmarkCommand:
    def execute(self, data):
        db.delete('bookmarks', {'id': data})
        return 'Bookmark deleted!'

class QuitCommad:
    def execute(self):
        sys.exit()

class ImportGitHubStarCommand:

    def _extract_bookmark_info(self, repo):
        return{
            'title': repo['name'],
            'url':   repo['html_url'],
            'notes': repo['description'],
        }
    
    def execute(self, data):
        bookmarks_imported = 0

        github_username = data['github_username']
        next_page_of_results = f'https://api.github.com/users/{github_username}/starred'
        while next_page_of_results:# continuees getting star result while more pages of results exist
            stars_response = requests.get(# gets the next page of results, using the right header Api to return timestamps
                next_page_of_results,
                headers={'Accept': 'application/vnd.github.v3.star+json'},
            )
            next_page_of_results = stars_response.links.get('next', {}).get('url')# The link hearder with rel=next contains thr link to the next page if available
            for repo_info in stars_response.json():
                repo = repo_info['repo']
                if data['preserve_timestamps']:
                    timestamp = datetime.strptime(
                        repo_info['starred_at'],
                        '%Y-%m-%dT%H:%M:%s2'
                    )
                else:
                    timestamp = None

                bookmarks_imported += 1
                AddBookmarkCommand().execute(
                    self._extract_bookmark_info(repo),
                    timestamp= timestamp
                )
        return f'Imported {bookmarks_imported} bookmarks from starred repo!'