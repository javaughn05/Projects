from flask import Flask, session, request, request, session

from flask_socketio import emit, join_room, leave_room

from cs50 import SQL
from .extensions import socketio

db = SQL("sqlite:///userbase.db")

# globally defined temporary dictionary of users for chatroom
users = {}

# globablly defined temporary queue of users; can edit in multiple functions
queue = []

# upon connection client side
@socketio.on("connect")
def handle_connect():
    # respond in terminal
    sid = request.sid
    print(f"Client {sid} connected!")

    # get the flask ID of the connected socket
    db.execute("UPDATE users SET sid = ? WHERE id = ?", sid, session["user_id"])

    # add the connected user to a queue
    # queue must occur before pairing in order to facilitate sufficient live matchmaking
    queue.append(sid)
    # keep track of queue in terminal
    print(f"Queue before: {queue}")

    # for now, when a queue has 4 users, match those users to a room
    if len(queue) >= 4: # at scale, this can be edited to a higher number or be based on a threshold
        # for developement, 4 users is sufficient in order to test

        # iterate throught the queue by the active socket ids
        for user_sid in queue:
            # current user_sid is the searching user
            print(f"Searching User: {user_sid}")

            # find an available room
            room_code = find_room(user_sid)
            # find the best available match (logic for filter_users defined later)
            match_sid = filter_users(user_sid)
            print(f"Found Match: {match_sid}")

            # the following code gives priority to users who have been in the queue the longest and automaticaly will connect their best user to their room
            # also prevents concurrency issues and race cases where both users match with the same user and / or the match_sid best match is another user
            # since the current user_sid has always been in the queue longer than their match_sid, their matchmaking is priortized

            # join the searching user
            join_room(room_code, sid=user_sid)
            # and the matched_user to the room
            join_room(room_code, sid=match_sid)

            # send notification to the client-side code that the client has been sent to a room
            emit("queued_success", room=room_code)

            print(f"User {user_sid} joined Room {room_code}")
            print(f"User {match_sid} joined Room {room_code}")

            # remove the two users from the search after they have been paired to a room
            # removed inside the loop because, if priority is given to users waiting longer, their match shouldn't match to a different room
            queue.remove(user_sid)
            queue.remove(match_sid)

            # update the rooms server backend database, filling the room before another searching user can access it
            db.execute("UPDATE rooms SET user1 = ?, user2 = ? WHERE code = ?", user_sid, match_sid, room_code)
            db.execute("UPDATE rooms SET size = ? WHERE code = ?", 2, room_code)

# after a user_joins the room
@socketio.on("user_join")
def handle_user_join(username):
    # function exists to pass the username value to the client-side code so a user's chosen username can appear next to their messages in the chat
    users[username] = request.sid

# if a user clicks the add-friend btn; when a user wants to add the user's contact
@socketio.on('add_friend')
def handle_add_friend():

    # the requesting user's socket id
    user_sid = request.sid
    # the requesting users flask id
    user_users = db.execute("SELECT id FROM users WHERE sid = ?", user_sid)
    user_fid = user_users[0]["id"]

    # the room code the user in
    room = db.execute("SELECT code FROM rooms WHERE user1 = ? OR user2 = ?", user_sid, user_sid)
    room_code = room[0]["code"]

    # the socket id of the person they are trying to add to their contact (person they are in the room with)
    friend = db.execute("SELECT CASE WHEN user1 = ? THEN user2 ELSE user1 END AS user FROM rooms WHERE code = ?", user_sid, room_code)
    friend_sid = friend[0]["user"]

    # the flask id of the friend
    friend_users = db.execute("SELECT id FROM users WHERE sid = ?", friend_sid)
    friend_fid = friend_users[0]["id"]

    # add a new contact row into friends
    db.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", user_fid, friend_fid)

    # the username of the person requesting the contact
    get_username = db.execute("SELECT username FROM users WHERE id = ?", user_fid)
    username = get_username[0]["username"]

    # message in chat
    message = "Added You!"

    # send to client code to send message in the chatroom
    emit("chat", {"message": message, "username": username}, room=room_code)

# handles when new messages are sent in the room
@socketio.on("new_message")
def handle_new_message(message):
    # the user's socket id
    sid = request.sid
    # room code of the user
    room = db.execute("SELECT code FROM rooms WHERE user1 = ? OR user2 = ?", sid, sid)
    room_code = room[0]["code"]
    print(room_code)
    print(f"New message: '{message}' in Room {room_code}")

    # reset username
    username = None
    # iterate through the users
    for user in users:
        # for each user's session id, see if equal to current sid
        if users[user] == request.sid:
            # set username equal to that sid
            username = user

    # Send the message to the recipient only
    emit("chat", {"message": message, "username": username}, room=room_code)

# handles disconnection of the client and the client they are paired with
@socketio.on("disconnect")
def handle_disconnect():
    # the disconecting user's socket id
    sid = request.sid
    print(f"Client disconnected: {sid}")
    # update their active status in the server database
    db.execute("UPDATE users SET sid = NULL WHERE sid = ?", sid)

    # remove the user from the queue
    if sid in queue:
        queue.remove(sid)
        print(f"Queue before: {queue}")

    # see if user has paired to a room yet
    room = db.execute("SELECT code FROM rooms WHERE user1 = ? OR user2 = ?", sid, sid)
    # if user is in a room (also means a user is with them because of other functons which ensure two users or none)
    if room:
        # room code
        room_code = room[0]["code"]
        print(room_code)

        # the socket id of the person they are in the room with
        other = db.execute("SELECT CASE WHEN user1 = ? THEN user2 ELSE user1 END AS user FROM rooms WHERE code = ?", sid, room_code)
        other_sid = other[0]["user"]
        print(other_sid)

        # update and remove the users from the room in the database
        db.execute("UPDATE rooms SET user1 = NULLIF(user1, ?), user2 = NULLIF(user2, ?) WHERE code = ?", sid, sid, room_code)
        db.execute("UPDATE rooms SET user1 = NULLIF(user1, ?), user2 = NULLIF(user2, ?) WHERE code = ?", other_sid, other_sid, room_code)

        # remove both users
        leave_room(room_code, sid=other_sid)
        leave_room(room_code)
        # update the size of the room in the database
        db.execute("UPDATE rooms SET size = 0 WHERE code = ?", room_code)

        # update the users table of the other user
        db.execute("UPDATE users SET sid = NULL WHERE sid = ?", other_sid)

        # send notification to client-side to redirect the other user in the room with the disconnecting user (updates html)
        emit('redirect', {'url': '/queue'}, room=other_sid)

# finds the requesting user (passes in their socket id) their best match
def filter_users(sid):
    # filter users
    # store sid and fid of searching user
    current_sid = sid
    fid_list = db.execute("SELECT id FROM users WHERE sid = ?", current_sid)
    fid = fid_list[0]["id"]

    # get community tag
    com_list = db.execute("SELECT community FROM users WHERE id = ?", fid)
    print(com_list)
    sid_community = com_list[0]["community"]

    # select all other users from the query from different communities
    placeholders = ", ".join("?" * len(queue))
    query = "SELECT id FROM users WHERE sid IN ({}) AND sid != ? AND community != ?".format(placeholders)
    active_users = db.execute(query, *queue, current_sid, sid_community)
    print(active_users)

    # get searching users scores
    user_scores = db.execute("SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism FROM scores WHERE user_id = ?", fid)

    difference = 0
    total_difference = 0
    td_list = {}
    idx = 0
    current_min = 0
    # iterate through active users, update the current minimum through iteration
    for user in active_users:
        if idx == 1:
            current_min = total_difference
        if idx > 1:
            if total_difference < current_min:
                current_min = total_difference
        idx += 1
        other_score = db.execute("SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism FROM scores WHERE user_id = ? AND user_id != ?", user["id"], fid)
        total_difference = 0
        # for each trait, invidually compare traits and add to the total difference
        for trait_score in other_score[0]:
            compare = int(other_score[0][trait_score])
            control = int(user_scores[0][trait_score])
            difference = abs(compare - control)
            total_difference += difference
            td_list[user["id"]] = total_difference
    # for the last user where the loop doesn't cover
    if total_difference < current_min:
                current_min = total_difference
    current_min = total_difference
    matching_user = 0
    # find matching user sid
    for user in td_list:
        if td_list[user] == current_min:
            matching_user = user
    match_list = db.execute("SELECT sid FROM users WHERE id = ?", matching_user)
    match_id = match_list[0]["sid"]
    print(current_min)
    return match_id


def find_room(sid):

    available_rooms = db.execute("SELECT code FROM rooms WHERE size < 2")
    print(available_rooms)

    # if available room code exists
    if available_rooms:
        this_room = available_rooms[0]
        room_code = this_room['code']

        session_sid = sid

        user1_field = db.execute("SELECT user1 FROM rooms WHERE code = ?", room_code)
        print(f"user1_field: {user1_field[0]["user1"]}")

        # if user1 is empty
        if user1_field[0]["user1"] == None:
            return room_code
        else:
            user1_sid = user1_field[0]["user1"]
            match_sid = filter_users(session_sid)
            # see if match_id is displaying
            print(f"match_sid: {match_sid}")
            if user1_sid == match_sid:
                return room_code
            else:
                # finds the room code of the match_sid
                match_room = db.execute("SELECT code FROM rooms WHERE user1 = ? OR user2 = ?", match_sid, match_sid)
                if match_room:
                    print(f"match_room: {match_room}")
                    match_code = match_room[0]["code"]
                    user1_match = db.execute("SELECT user1 FROM rooms WHERE code = ?", match_code)
                    if user1_match[0]["user1"] == None:
                        return match_code
                    else:
                        return match_code
                else:
                    empty_rooms = db.execute("SELECT code FROM rooms WHERE size = 0")
                    print(f"match_room: {empty_rooms}")
                    if empty_rooms:
                        empty_code = empty_rooms[0]["code"]
                        print(f"empty_code: {empty_code}")
                        return empty_code
    else:
        print("No available rooms")
        db.execute("INSERT INTO rooms DEFAULT VALUES")
        new_room = db.execute("SELECT code FROM rooms WHERE size = 0")
        new_room_code = new_room[0]
        return new_room_code
