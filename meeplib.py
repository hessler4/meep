"""
meeplib - A simple message board back-end implementation.

Functions and classes:

 * u = User(username, password) - creates & saves a User object.  u.id
     is a guaranteed unique integer reference.

 * m = Message(title, post, author) - creates & saves a Message object.
     'author' must be a User object.  'm.id' guaranteed unique integer.

 * get_all_messages() - returns a list of all Message objects.

 * get_all_users() - returns a list of all User objects.

 * delete_message(m) - deletes Message object 'm' from internal lists.

 * delete_user(u) - deletes User object 'u' from internal lists.

 * get_user(username) - retrieves User object for user 'username'.

 * get_message(msg_id) - retrieves Message object for message with id msg_id.

"""
import pickle
import sqlite3 as lite
import sys

__all__ = ['Message', 'get_all_messages', 'get_message', 'delete_message',
           'User', 'get_user', 'get_all_users', 'delete_user']

###
# internal data structures & functions; please don't access these
# directly from outside the module.  Note, I'm not responsible for
# what happens to you if you do access them directly.  CTB

# a dictionary, storing all messages by a (unique, int) ID -> Message object.
_messages = {}

def _get_next_message_id():
    if _messages:
        return max(_messages.keys()) + 1
    return 0

# a dictionary, storing all users by a (unique, int) ID -> User object.
_user_ids = {}

# a dictionary, storing all users by username
_users = {}

def _get_next_user_id():
    if _users:
        return max(_user_ids.keys()) + 1
    return 0

def _reset():
    """
    Clean out all persistent data structures, for testing purposes.
    """
    global _messages, _users, _user_ids
    _messages = {}
    _users = {}
    _user_ids = {}

def save():
	print "SAVING"
	obj = _messages, _users, _user_ids
	#print _messages
	fp = open('save.pickle', 'wb')
	pickle.dump(obj, fp)
	fp.close()
	#for thing in _user_ids:
	#       print thing
	
def load():
    con = lite.connect('test.db')
    cur = con.cursor()
    try:
        with con:
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM Users")
            rows = cur.fetchall()
            for row in rows:
                print "%s %s" % (row["Name"], row["Password"])
                User(row["Name"], row["Password"])

            cur.execute("SELECT * FROM Messages")
            rows = cur.fetchall()
            for row in rows:
                #print "%s %s %s %s" % (row["Title"], row["Post"], row["Author"], row["Parent"])
                Message(row["Title"], row["Post"], get_user(row["Author"]), int(row["Parent"]))

	    print "printing messages"
	    for m in get_all_messages():
	        print m.author.username, m.title, m.post, m.parent, m.id
	#####################################
#       global _messages, _users, _user_ids
#       fp = open('save.pickle', 'rb')
#       _messages, _users, _user_ids = pickle.load(fp)
#       print _messages
#       fp.close() 

#    except IOError:  # file does not exist/cannot be opened
#       print "Error opening 'save.pickle'"
	
    except lite.Error, e:

       print "Error %s:" % e.args[0]
       sys.exit(1)
	
    finally:

       if con:
          con.close()
###

class Message(object):
    """
    Simple "Message" object, containing title/post/author.

    'author' must be an object of type 'User'.

    """
    def __init__(self, title, post, author, parent):
        self.title = title
        self.post = post
        self.parent = parent

        assert isinstance(author, User)
        self.author = author

        self._save_message()

    def _save_message(self):
        self.id = _get_next_message_id()

        # register this new message with the messages list:
        _messages[self.id] = self

def get_all_messages(sort_by='id'):
    return _messages.values()

def get_message(id):
    return _messages[id]

def delete_message(msg):
    assert isinstance(msg, Message)
    del _messages[msg.id]

###

class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self._save_user()

    def _save_user(self):
        self.id = _get_next_user_id()

        # register new user ID with the users list:
        _user_ids[self.id] = self
        _users[self.username] = self

def get_user(username):
    return _users.get(username)         # return None if no such user

def get_all_users():
    return _users.values()

def delete_user(user):
    del _users[user.username]
    del _user_ids[user.id]
