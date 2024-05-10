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

$(document).on('click', '.btn-edit', function (event) {
    event.preventDefault();
    const container = $(this).closest('form');
    const title = container.find('.title');
    const content = container.find('p');
    const deleteBtn = container.find('.btn-delete');
    
    title.replaceWith(`<input type="text" class="form-control" value="${title.text()}" required>`);
    content.replaceWith(`<textarea class="form-control" rows="3" required>${content.text()}</textarea>`);
    deleteBtn.addClass('d-none');
    $(this).text('💾').toggleClass('btn-edit btn-save');
});

$(document).on('click', '.btn-save', function (event) {
    event.preventDefault();
    const container = $(this).closest('form');
    const title = container.find('input');
    const content = container.find('textarea');
    const deleteBtn = container.find('.btn-delete');

    axios.post('/edit', {
        id: container.attr('name'),
        title: title.val(),
        content: content.val()
    }).then(res => {
        const msg = res.data.msg;
        toggleAlert('#editArticleAlert', msg, msg === "Success!");
    });
    title.replaceWith(`<h3 class="title">${title.val()}</h3>`);
    content.replaceWith(`<p>${content.val()}</p>`);
    deleteBtn.removeClass('d-none');
    $(this).text('✏️').toggleClass('btn-save btn-edit');
});

$('.btn-delete-article').click(function (event) {
    event.preventDefault();
    axios.post('/delete', {
        type: 'article',
        id: $(this).closest('form').attr('name')
    }).then(res => {
        const msg = res.data.msg;
        toggleAlert('#editArticleAlert', msg, msg === "Success!");
    });
});

$('.btn-delete-comment').click(function (event) {
    event.preventDefault();
    axios.post('/delete', {
        type: 'comment',
        id: $(this).attr('name')
    }).then(res => {
        const msg = res.data.msg;
        toggleAlert('#deleteCommentAlert', msg, msg === "Success!");
        if (msg === "Success!") {
            $(this).closest('.card').remove();
        }
    });
});

function toggleAlert(selector, message, isSuccess) {
    $(selector)
        .text(message)
        .toggleClass('alert-success', isSuccess)
        .toggleClass('alert-danger', !isSuccess)
        .removeClass('d-none');
}
