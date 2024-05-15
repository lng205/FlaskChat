const socket = io();
const username = Cookies.get("username");
let room_id = parseInt(Cookies.get("room_id"));
// get user role


    changeBoxDisplay(!!room_id);
    $('#addFriendForm').submit(handleAddFriend);
    $('#startChatForm').submit(handleStartChat);
    $('.friend-item').click(handleStartChat);
    $('#messageInputForm').submit(sendMessage);
    $('.handle-request-button').click(handleFriendRequest);
    $('.remove-button').click(removeFriend);
    $('#leaveButton').click(leaveChat);
// get the user mute status from class the_mute_status
var isMuted = false;
isMuted = $('.the_mute_status').text() === 'muted';
if (isMuted) {
        leaveChat();
    }
//display current room id in id getcurrentroom
socket.on('current_room', room_id => {
    document.getElementById('getcurrentroom').textContent = room_id;
}
);

// Socket event handlers
socket.on("incoming", (msg, color = "blue") => {
     $("#messageBox").append($("<p class='mb-0'></p>").text(msg).css("color", color));
});

socket.on("status_update", msg => {
    if (msg.online) {
        $(`.friend-item[name="${msg.username}"] .online-status`).css('color', 'green');
    }
    else {
        $(`.friend-item[name="${msg.username}"] .online-status`).css('color', 'red');
    }
})

socket.on("friend_change", () => window.location.reload());

socket.on("add_friend_response", res => {
    toggleAlert('#addFriendAlert', res, res === "Success!");
});
socket.on("get_all_rooms", function(data) {
    var roomsList = document.getElementById('getrooms_all');
    roomsList.innerHTML = '';  
    console.log("Rooms received:", data);
    
    // Ensure data is an array
    if (Array.isArray(data)) {
        data.forEach(room => {
            var roomItem = document.createElement('li');
            roomItem.textContent = room;
            roomsList.appendChild(roomItem);
        });
    } else {
        console.error('Invalid rooms data:', data);
    }
});


socket.on('update_members', function(data) {
    console.log("Received update_members event with data:", data); 
    let membersList = document.getElementById('roomMembers');
    if (data) {
        membersList.innerHTML = '';  // Clear existing members list
        console.log("Updating members list:", data.members);

        data.members.forEach(member => {
            let memberItem = document.createElement('span');
            memberItem.textContent = member;
            membersList.appendChild(memberItem);
        });
    } else {
        console.log("No members data received or members list is empty");
    }
});


// Form submission handlers
function handleAddFriend(event) {
    event.preventDefault();
    const input = $('input', this);
    socket.emit("add_friend", username, input.val());
    input.val("");
}

function handleStartChat(event) {
    socket.emit("current_room");
    const nameAttr = $(this).attr('name');
    // if user is muted, then return a message to user
    if (isMuted) {
        alert('You are muted, you cannot chat with others');
        return;
    }
    if (nameAttr) {
        startChat(nameAttr);
    }
    else {
        const input = $('input', this);
        event.preventDefault();
        startChat(input.val());
        input.val("");
    }
}

function sendMessage(event) {
    event.preventDefault();
    const input = $('input', this);
    socket.emit("send", username, input.val(), room_id);
    input.val("");
}

function handleFriendRequest(event) {
    socket.emit(
        "handle_friend_request",
        username,
        event.target.name,
        event.target.value
    )}

function removeFriend(event) {
    socket.emit("remove_friend", username, event.target.name)
}

function leaveChat() {
    Cookies.remove("room_id");
    socket.emit("leave", username, room_id);
    changeBoxDisplay(false);
}

// Utility functions
function startChat(receiver) {
    socket.emit("current_room");
    socket.emit("join", username, receiver, res => {
        if (typeof res !== "number") {
            alert(res);
            return;
        }
        room_id = res;
        Cookies.set("room_id", room_id);
        changeBoxDisplay(true);
    });
}

function changeBoxDisplay(isChatStarted) {
    $("#messageInputForm").toggleClass("d-none", !isChatStarted);
    $("#startChatForm").toggleClass("d-none", isChatStarted);
}

function toggleAlert(selector, message, isSuccess) {
    $(selector)
        .text(message)
        .toggleClass('alert-success', isSuccess)
        .toggleClass('alert-danger', !isSuccess)
        .removeClass('d-none');
}
document.addEventListener('DOMContentLoaded', function() {
    setupPopups();
});
function setupPopups() {
    var helpBtn = document.getElementById('helpBtn');
    var closePopup = document.getElementById('closePopup');
    var helpPopup = document.getElementById('helpPopup');

    if (helpBtn && closePopup) {
        helpBtn.addEventListener('click', function() {
            document.getElementById('helpPopup').style.display = 'block';
        });
        closePopup.addEventListener('click', function() {
            document.getElementById('helpPopup').style.display = 'none';
        });
        helpPopup.addEventListener('click', function(event) {
            document.getElementById('helpPopup').style.display = 'none';
        });
        document.addEventListener('keydown', function(event) {
            if (event.key === "Escape") {
                document.getElementById('helpPopup').style.display = 'none';
            }
        });
    }
}