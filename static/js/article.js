$('#newArticleForm').submit(function (event) {
    event.preventDefault();
    const title = $('#newArticleTitle').val();
    const content = $('#newArticleContent').val();
    axios.post('/article', {
        title: title,
        content: content
    }).then(res => {
        const msg = res.data.msg;
        toggleAlert('#newArticleAlert', msg, msg === "Success!");
    })
    // Clear the input fields
    $('#newArticleTitle').val('');
    $('#newArticleContent').val('');
})

function toggleAlert(selector, message, isSuccess) {
    $(selector)
        .text(message)
        .toggleClass('alert-success', isSuccess)
        .toggleClass('alert-danger', !isSuccess)
        .removeClass('d-none');
}
