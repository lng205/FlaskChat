const socket = io();
const username = Cookies.get("username");
let room_id = parseInt(Cookies.get("room_id"));

$(document).ready(() => {
    changeBoxDisplay(!!room_id);

    $('#addFriendForm').submit(handleAddFriend);
    $('#startChatForm').submit(handleStartChat);
    $('.friend-item').click(handleStartChat);
    $('#messageInputForm').submit(sendMessage);
    $('.handle-request-button').click(handleFriendRequest);
    $('.remove-button').click(removeFriend);
    $('#leaveButton').click(leaveChat);
});

// Socket event handlers
socket.on("incoming", (msg, color = "black") => {
    $("#message_box").append($("<p class='mb-0'></p>").text(msg).css("color", color));
});

socket.on("status_update", msg => {
    if (msg.online) {
        $(`.friend-item[name="${msg.username}"] span`).css('color', 'green');
    }
    else {
        $(`.friend-item[name="${msg.username}"] span`).css('color', 'red');
    }
})

socket.on("friend_change", () => window.location.reload());

socket.on("add_friend_response", res => {
    toggleAlert('#addFriendAlert', res, res === "Success!");
});

// Form submission handlers
function handleAddFriend(event) {
    event.preventDefault();
    const input = $('input', this);
    socket.emit("add_friend", username, input.val());
    input.val("");
}

function handleStartChat(event) {
    const nameAttr = $(this).attr('name');
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
