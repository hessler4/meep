import meeplib
import traceback
import cgi

def initialize():
    # create a default user
    u = meeplib.User('test', 'foo')

    # create a single message
    meeplib.Message('my title', 'This is my message!', u, -1)

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
             Title: <input type='text' name='title'><br>
             Message:<input type='text' name='message'><br>
             <input type='hidden' name='parent_id' value='%d'>
             <input type='submit'></form>
             </div>""" % (m.id,m.id,m.id,m.id))
    s.append('<hr>')
    return s
	
class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])

        username = 'test'

        return ["""you are logged in as user: %s.<p><a href='/m/add'>Add a message</a><p><a href='/login'>Log in</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (username,)]

    def login(self, environ, start_response):
        # hard code the username for now; this should come from Web input!
        username = 'test'

        # retrieve user
        user = meeplib.get_user(username)

        # set content-type
        headers = [('Content-type', 'text/html')]
        
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def logout(self, environ, start_response):
        # does nothing
        headers = [('Content-type', 'text/html')]

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"
		
    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()

        s = []
        listed = set()
        for m in messages:
	        if m.id not in listed:
		        s.extend(retrieve_message(m))
		        currid = m.id
		        deepest_node = m
		        while True:
			        found = False
			        nests = 0
			        for child in messages:
				        #print('looping')
				        if child.parent == currid and child.id not in listed:
					        found = True
					        nests+=1
					        parent_id = currid
					        for x in xrange(0, nests):
					            s.append('<ul>')

					        s.extend(retrieve_message(child))

					        for y in xrange(0, nests):
					            s.append('</ul>')

					        listed.add(child.id)
					        currid = child.id
					        deepest_node = child
			
			        if found == False: break
		        currid = deepest_node.parent
		        if currid == -1: break 
			
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

        meeplib.delete_message(msg)
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message deleted"]
      
    #def reply_message(self, environ, start_response):
        
    def add_message(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)

        return """<form action='add_action' method='POST' name='heythere'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='hidden' name='parent_id' value='%d'><input type='submit'></form>""" % -1

    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        parent = int(form['parent_id'].value)
        
        username = 'test'
        user = meeplib.get_user(username)
        
        new_message = meeplib.Message(title, message, user, parent)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message added"]
    
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
                      '/logout': self.logout,
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
