const socket = io();
const username = Cookies.get("username");
let room_id = Cookies.get("room_id");
changeBoxDisplay(!!room_id);

$('#addFriendForm').submit(handleAddFriend);
$('#joinRoomForm').submit(handleJoinRoom);
$('#createRoomBtn').click(handleCreateRoom);
$('.friend-item').click(handleStartChat);
$('#messageInputForm').submit(sendMessage);
$('.handle-request-button').click(handleFriendRequest);
$('.remove-button').click(removeFriend);
$('#leaveButton').click(leaveChat);
$('#helpBtn').click(() => $('#helpPopup').show());
$('#closePopup').click(() => $('#helpPopup').hide());

// Socket event handlers
socket.on("incoming", (msg, color = "black") => {
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

socket.on("room_member_change", members => {
    $("#roomMembers").text(members);
})

// Element event handlers
function handleAddFriend(event) {
    event.preventDefault();
    const input = $('input', this);
    socket.emit("add_friend", username, input.val());
    input.val("");
}

function handleJoinRoom(event) {
    event.preventDefault();
    const input = $('input', this).val();
    socket.emit("join_room", username, input, res => {
        if (res === "Success!") {
            room_id = input;
            Cookies.set("room_id", room_id);
            changeBoxDisplay(true);
        }
        else
        {
            toggleAlert('#joinRoomAlert', res, false);
        }
    });
    $('input', this).val("");
}

function handleCreateRoom() {
    socket.emit("create_room", username, res => {
        if (typeof res !== "number") {
            toggleAlert('#joinRoomAlert', res, false);
            return;
        }
        room_id = res;
        Cookies.set("room_id", room_id);
        changeBoxDisplay(true);
    });
}

function handleStartChat() {
    const isMuted = $('.the_mute_status').text() === 'muted';
    if (isMuted) {
        alert('You are muted, you cannot chat with others');
        return;
    }

    const receiver = $(this).attr('name');
    socket.emit("private_chat", username, receiver, res => {
        if (typeof res !== "number") {
            alert(res);
            return;
        }
        room_id = res;
        Cookies.set("room_id", room_id);
        changeBoxDisplay(true);
    });
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
    )
}

function removeFriend(event) {
    socket.emit("remove_friend", username, event.target.name)
}

function leaveChat() {
    Cookies.remove("room_id");
    socket.emit("leave", username, room_id);
    changeBoxDisplay(false);
}

// Utility functions
function changeBoxDisplay(isChatStarted) {
    $("#messageInputForm").toggleClass("d-none", !isChatStarted);
    $("#joinRoomForm").toggleClass("d-none", isChatStarted);
}

function toggleAlert(selector, message, isSuccess) {
    $(selector)
        .text(message)
        .toggleClass('alert-success', isSuccess)
        .toggleClass('alert-danger', !isSuccess)
        .removeClass('d-none');

    setTimeout(() => $(selector).addClass('d-none'), 3000);
}
