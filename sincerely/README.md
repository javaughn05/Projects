***SEE REQUIREMENTS AT BOTTOM BEFORE USING*** Be sure to install socketIO and Flask-SocketIO to your terminal before running.

1. (a) In order to first open the project, navigate to the "sincerely" directory (cd sincerely) and run it using (python run.py). When you first join, you should see the nav bar at the top with a link for the "Register" page. You can click on this page and add your own account by filling out each field and pressing submit. When registering, be sure to include an email with a valid Ivy-League school domain (@yale.edu, @harvard.edu, etc.). You will then automatically be logged in, where you can skip to step 2

1. (b) You may also directly click the login button and login into an already existing account (see SQL userbase.db for existing accounts -- for testing purposes, for any already existing accounts, I set the passwords to the second part of the email handle ex:
email: john.doe@yale.edu
username: john
password: apple123 )
Existing accounts already have scores registered, so skip to step 3

2. When you login, you should first click the "Scores" button and add your Big Five personality test results (any numbers 0-100). Within the "scores" page, add integers between 0-100 to each one of the input fields. After you've filled these inputs out, press the submit button at the bottom. This will automatically send you to the queue page.

3. Input any username you would like to talk as (intended to keep users more anonymous as they can change their name everytime they queue instead of being restricted to one username which they assigned themselves when they first registered).Then click "go," and if all steps were followed, a spinning circle should pop up while the user waits to be paired. ***After following all of these steps in this order, continue***

4. Due to the fact that this project is running through flask, to test, you will need to reopen the link from the terminal and logout. This is because flask remembers users from the same IP address, but because the app is being hosted from a local server, you need to reiniate the logout and login. You can test this app by logging into a new account, and following all of the steps above again 3 more times.
*****You can also, alternatively, open 4 different browsers when logged out in the very beginning. Either way, you need to queue as the logged-in user before logging in as another user.
**If you decide to register 4 new users, be sure they are apart of different schools. The app avoids pairing users from the same community intentionally**

5. Once users 4 different accounts have been queued, users will be paired. In order to send messages, enter messages in the message input and click the
"enter" button.

6. A users contact can be added to a SQL database if you click the "add friend" button while inside a paired chatroom

7. If you disconnect, it will disconnect both users (to ensure users are never in a room by themselves)

***IMPORTANT*** When testing, make sure you queue (click "go") while signed into one account **BEFORE** trying to reopen the local server and log into another account. Otherwise, the flask id of one browser will apply to all open browsers, failing to update the socket ids of connected users in the database (since users only connect when you click "go").

After entering the queue from 4 different accounts 4 different times, each browser will be paired with a user. Two users can chat in a chat room, and add one another to a contact list by clicking the "add friend" button at the top. Both users can do this. These contacts (based on flask ids) are added to a databse that can be used later to create direct messages, cross-reference scores of befriended users in order to make better matches, etc.

**POTENTIAL ERRORS**
- First, when you click a button on a page and nothing occurs, you may have to simply click that button once or twice more. This lag is likely a result of
  being hosted on a local server where lots of information is being processed.

- If an error does occur because multiple browsers are open before queuing or some flask id is not being recognized, be sure to double check the back-end
  SQL database (I used phpLiteAdmin) and ensure the "sid" field in the users table and the user1 / user2 fields in the rooms table are set to NULL. If not, simply click edit on the row with the wrong fields and check the "NULL" box. You can restart from there.

Be sure to install the requirments below.

***REQUIREMENTS***

bidict                             0.22.1 (pip install bidict)
Flask                              3.0.0
Flask-Session                      0.5.0
Flask-SocketIO                     5.3.6 (pip install flask-socketio)
greenlet                           3.0.1 (pip install greenlet)
Jinja2                             3.1.2
MarkupSafe                         2.1.3
python-engineio                    4.8.0
python-socketio                    5.10.0 (pip install python-socketio)
six                                1.16.0
Werkzeug                           3.0.1 (pip install Werkzeug)


YOUTUBE LINK: https://youtu.be/jt0Jrn2XOKg













