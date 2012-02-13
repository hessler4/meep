import meeplib
import traceback
import cgi
import cookie

def initialize():
    # create a default user
    # u = meeplib.User('test', 'foo')

    # create a single message
    # meeplib.Message('my title', 'This is my message!', u, -1)
    
    # load previous data
    meeplib.load()

    # done.

def retrieve_message(m):
    s = []
    s.append('id: %d<p>' % (m.id,))
    s.append('title: %s<p>' % (m.title))
    s.append('message: %s<p>' % (m.post))
    s.append('author: %s<p>' % (m.author.username))
    s.append(
             """<form action='delete' method='GET'>
                <input type='hidden' value='%d' name='id'>
                <input type='submit' value='Delete'></form>""" % (m.id,))
    s.append(
             """<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js"></script>
             <script type="text/javascript">
             $(document).ready(function() { 
                 $(reply_form%d).hide();
             });
             function toggleDiv(divId) {
                 $("#"+divId).toggle();
             }
             function showonlyone(thechosenone) {
                 $('div[name|="reply"]').each(function(index) {
                     if ($(this).attr("id") == thechosenone) {
                         $(this).slideDown(600);
		             }
			         else {
			             $(this).slideUp(600);
			         }
                 });
             }
             </script><a href="javascript:showonlyone('reply_form%d');" <html><body><button type="button">Reply</button></body></html></a>
             <div name="reply" id="reply_form%d"><form action='add_action' method='POST' name='heythere'>
             Title:<input type='text' name='title' value='RE: %s'><br>
             Message:<input type='text' name='message'><br>
             <input type='hidden' name='parent_id' value='%d'>
             <input type='submit'></form>
             </div>""" % (m.id, m.id, m.id, m.title, m.id))
    s.append('<hr>')
    return s

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def __init__(self):
        self.username = None

    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])
        s=["""Please login to create and delete messages<p><a href='/login'>Log in</a><p><a href='/create_user'>Create a New User</a><p><a href='/m/list'>Show messages</a>"""]
        if self.username is not None:
            s = ["""you are logged in as user: %s.<p><a href='/m/add'>Add a message</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (self.username,)]
        return s

    def login(self, environ, start_response):
        headers = [('Content-type', 'text/html')]

        print "do i have input?", environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        print "form", form

        try:
            username = form['username'].value
            # retrieve user
            print "we gots a username", username
        except KeyError:
            username = ''
            print "no user input"

        try:
            password = form['password'].value
            print "we gots a password", password
        except KeyError:
            password = ''
            print 'no password input'

        s=[]

        ##if we have username and password
        if username != '' and password != '':
            user = meeplib.get_user(username)
            if user is not None and user.password == password:
                ## send back a redirect to '/'
                cookie_name, cookie_val = \
				meepcookie.make_set_cookie_header('username', user.username)
				headers.append((cookie_name, cookie_val))
                k = 'Location'
                v = '/'
                headers.append((k, v))
                self.username = username
            elif user is None:
                s.append('''Login Failed! <br>
                    The Username you provided does not exist<p>''')

            else:
                ## they messed up the password
                s.append('''Login Failed! <br>
                    The Username or Password you provided was incorrect<p>''')

        ##if we have username or password but not both
        elif username != '' or password != '':
            s.append('''Login Failed! <br>
                    The Username or Password you provided was incorrect<p>''')

        start_response('302 Found', headers)

        ##if we have a valid username and password this is not executed
        s.append('''
                    <form action='login' method='post'>
                        <label>username:</label> <input type='text' name='username' value='%s'> <br>
                        <label>password:</label> <input type='password' name='password'> <br>
                        <input type='submit' name='login button' value='Login'></form>

                        <p><a href='/create_user'>Create a New User</a>''' %(username))
        return [''.join(s)]

    def logout(self, environ, start_response):

        self.username =  None

        headers = [('Content-type', 'text/html')]

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def create_user(self, environ, start_response):
        headers = [('Content-type', 'text/html')]

        print "do i have input?", environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        print "form", form

        try:
            username = form['username'].value
            # retrieve user
            print "we gots a username", username
        except KeyError:
            username = ''
            print "no user input"

        try:
            password = form['password'].value
            print "we gots a password", password
        except KeyError:
            password = ''
            print 'no password input'

        try:
            password2 = form['password_confirm'].value
            print "we gots a password", password
        except KeyError:
            password2 = ''
            print 'no password confirmation'

        s=[]

        ##if we have username and password and confirmation password
        if username != '':
            user = meeplib.get_user(username)
            ## user already exists
            if user is not None:
                s.append('''Creation Failed! <br>
                    User already exists, please use a different Username<p>''')
            ## user doesn't exist but they messed up the passwords
            elif password == '':
                s.append('''Creation Failed! <br>
                    Please fill in the Password field<p>''')
            elif password != password2:
                s.append('''Creation Failed! <br>
                    The Password and Confirmation Password you provided did not match<p>''')
            else:
                u = meeplib.User(username, password)
                meeplib.save()
                ## send back a redirect to '/'
                k = 'Location'
                v = '/'
                headers.append((k, v))
                self.username = username
        elif password != '' or password2 != '':
            s.append('''Creation Failed! <br>
            Please provide a Username<p>''')


        start_response('302 Found', headers)

        ##if we have a valid username and password this is not executed
        s.append('''
                    <form action='create_user' method='post'>
                        <label>username:</label> <input type='text' name='username' value='%s'> <br>
                        <label>password:</label> <input type='password' name='password' value='%s'> <br>
                        <label>confirm password:</label> <input type='password' name='password_confirm' value='%s'> <br>
                        <input type='submit' name='create user button' value='Create'></form>''' %(username, password, password2))
        return [''.join(s)]

    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()

        s = []
        listed = set()
        for m in messages:
	        if m.id not in listed:
		        s.extend(retrieve_message(m))
		        curr_id = m.id
		        deepest_node = m
		        indent = 0
		        while True:
			        for child in messages:
				        if child.parent == curr_id and child.id not in listed:
					        indent+=1
					        for x in xrange(0, indent):
					            s.append('<ul>')

					        s.extend(retrieve_message(child))

					        for y in xrange(0, indent):
					            s.append('</ul>')

					        listed.add(child.id)
					        curr_id = child.id
					        deepest_node = child
					
			        curr_id = deepest_node.parent
			        if curr_id == -1: break
			        indent -= 1 
			        deepest_node = meeplib.get_message(curr_id)
			         
			
        listed.clear()
        s.append("<a href='../../'>index</a>")
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        #print("".join(s))
        return ["".join(s)]

    def delete_message(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        msgid = int(form['id'].value)
		
        msg = meeplib.get_message(msgid)

        messages = meeplib.get_all_messages()

        if msg.parent == -1:
	        for child in messages:
		        if child.parent == msgid:
			        child.parent = -1
        else:
			for child in messages:
				if child.parent == msgid:
					child.parent = msg.parent
		
        meeplib.delete_message(msg)

        meeplib.save()
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message deleted"]
      
    #def reply_message(self, environ, start_response):
        
    def add_message(self, environ, start_response):
        if self.username is None:
            headers = [('Content-type', 'text/html')]
            start_response("302 Found", headers)
            return ["You must be logged in to user this feature <p><a href='/login'>Log in</a><p><a href='/m/list'>Show messages</a>"]

        headers = [('Content-type', 'text/html')]

        start_response("200 OK", headers)

        return """<form action='add_action' method='POST' name='heythere'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='hidden' name='parent_id' value='%d'><input type='submit'></form>""" % -1

    def add_message_action(self, environ, start_response):
        if self.username is None:
            headers = [('Content-type', 'text/html')]
            start_response("302 Found", headers)
            return ["You must be logged in to user this feature <p><a href='/login'>Log in</a><p><a href='/m/list'>Show messages</a>"]


        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        parent = int(form['parent_id'].value)
        
        user = meeplib.get_user(self.username)
        
        new_message = meeplib.Message(title, message, user, parent)

        meeplib.save()

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]
    
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/create_user': self.create_user,
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/delete': self.delete_message
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        fn = call_dict.get(url)

        if fn is None:
            start_response("404 Not Found", [('Content-type', 'text/html')])
            return ["Page not found."]

        try:
            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]
