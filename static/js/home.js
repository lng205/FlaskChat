const socket = io();
const username = Cookies.get("username");
let room_id = parseInt(Cookies.get("room_id"));

$(document).ready(() => {
    changeBoxDisplay(!!room_id);

    $('#message_box').css('height', '400px');
    $('#addFriendForm').submit(handleAddFriend);
    $('#startChatForm').submit(handleStartChat);
    $('#messageInputForm').submit(sendMessage);
    $('#leaveButton').click(leaveChat);

    // Delegate click events for dynamic elements
    $(document).on('click', '.accept_button', e => processFriendRequest(e.target.name, true));
    $(document).on('click', '.reject_button', e => processFriendRequest(e.target.name, false));
    $('.friend-item').click(e => joinRoom(e.target.name));
});

// Socket event handlers
socket.on("incoming", (msg, color = "black") => {
    $("#message_box").append($("<p class='mb-0'></p>").text(msg).css("color", color));
});

// Form submission handlers
function handleAddFriend(event) {
    event.preventDefault();
    axios.post(this.action, new FormData(this))
        .then(res => toggleAlert('#addFriendAlert', res.data.message, res.data.message === "Success!"))
        .catch(() => window.location.reload());
}

function handleStartChat(event) {
    event.preventDefault();
    joinRoom($('#startChatName').val());
}

function sendMessage(event) {
    event.preventDefault();
    const message = $('#message').val();
    socket.emit("send", username, message, room_id);
    $('#message').val("");
}

function leaveChat() {
    Cookies.remove("room_id");
    socket.emit("leave", username, room_id);
    changeBoxDisplay(false);
}

// Utility functions
function joinRoom(receiver) {
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

function processFriendRequest(friend, accept) {
    axios.post("/home/process", { username, friend, accept })
        .then(res => res.data === "Success!" ? location.reload() : alert(res.data));
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
