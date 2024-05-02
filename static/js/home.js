$(document).ready(() => {
    $("#message").keyup(e => e.key == "Enter" && send());
    $("#receiver").keyup(e => e.key == "Enter" && join_room());
    $('#join_room_button').click(join_room);
    
    $('.friend_item').click(e => startChatWith(e.target.getAttribute('name')));
    $('.accept_button').click(e => processFriendRequest(e.target.getAttribute('name'), true));
    $('.reject_button').click(e => processFriendRequest(e.target.getAttribute('name'), false));

    $('#send_button').click(send);
    $('#leave_button').click(leave);
    // room_id is undefined if the user hasn't joined a room
    // we early return in this case
    if (Cookies.get("room_id") == undefined) {
        return;
    }

    // the user has already joined an existing room
    // we'll display the message box, instead of the "Chat with: " box
    $("#chat_box").hide();
    $("#input_box").show();
    room_id = parseInt(Cookies.get("room_id"));
})

let username = Cookies.get("username");

// initializes the socket
const socket = io();

// an incoming message arrives, we'll add the message to the message box
socket.on("incoming", (msg, color = "black") => {
    add_message(msg, color);
})

// we'll send the message to the server by emitting a "send" event
function send() {
    let message = $("#message").val();
    $("#message").val("");
    socket.emit("send", username, message, room_id);
}

// we emit a join room event to the server to join a room
function join_room() {
    socket.emit("join", username, $("#receiver").val(), (res) => {
        // res is a string with the error message if the error occurs
        // this is a pretty bad way of doing error handling, but watevs
        if (typeof res != "number") {
            alert(res);
            return;
        }

        // set the room id variable to the room id returned by the server
        room_id = res;
        Cookies.set("room_id", room_id);

        // now we'll show the input box, so the user can input their message
        $("#chat_box").hide();
        $("#input_box").show();
    });

}

// function when the user clicks on "Leave Room"
// emits a "leave" event, telling the server that we want to leave the room
function leave() {
    Cookies.remove("room_id");
    socket.emit("leave", username, room_id);
    $("#input_box").hide();
    $("#chat_box").show();
}

// function to add a message to the message box
// called when an incoming message has reached a client
function add_message(message, color) {
    let box = $("#message_box");
    let child = $('<p></p>').text(message).addClass("message").css("color", color);
    box.append(child);
}

// Create a post request to the server to add a friend
function addFriend() {
    const new_friend = $("#new_friend_username").val();
    axios.post("/home/add", {
        username: username,
        friend: new_friend
    }).then((res) => {
        if (res.data == "Success") {
            location.reload();
        } else {
            alert(res.data);
        }
    });
}

// Create a post request process a friend request
function processFriendRequest(friend, accept) {
    axios.post("/home/process", {
        username: username,
        friend: friend,
        accept: accept
    }).then((res) => {
        if (res.data == "Success") {
            location.reload();
        } else {
            alert(res.data);
        }
    });
}

function startChatWith(friend) {
    // Set the receiver input to the friend's name
    $("#receiver").val(friend);
    // Directly call join_room to start the chat
    join_room();
}