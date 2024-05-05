$('#newArticleSubmitButton').click(() => {
    axios.post('/article', {
        text: $('#newArticleText').val()
    }).then(res => {
        const msg = res.data.msg;
        toggleAlert('#newArticleAlert', msg, msg === "Success!");
    })
    $('#newArticleText').val('');
});

function toggleAlert(selector, message, isSuccess) {
    $(selector)
        .text(message)
        .toggleClass('alert-success', isSuccess)
        .toggleClass('alert-danger', !isSuccess)
        .removeClass('d-none');
}
