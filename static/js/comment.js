$('#newCommentForm').submit(function (event) {
    event.preventDefault();
    const content = $('#newCommentContent').val();
    axios.post(window.location.href, {
        content: content
    }).then(res => {
        const msg = res.data.msg;
        toggleAlert('#newCommentAlert', msg, msg === "Success!");
    })
    // Clear the input fields
    $('#newCommentTitle').val('');
    $('#newCommentContent').val('');
})

function toggleAlert(selector, message, isSuccess) {
    $(selector)
        .text(message)
        .toggleClass('alert-success', isSuccess)
        .toggleClass('alert-danger', !isSuccess)
        .removeClass('d-none');
}
