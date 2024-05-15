$('.btn-change').click(function () {
    const button = $(this);
    const username = button.data('username');
    const type = button.closest('div').find('select').val();
    axios.post('/admin', {
        username: username,
        type: type
    }).then(res => {
        $('.alert').text(res.data.msg).removeClass('d-none');
    });
});

// Attach event handler for toggling mute status
$('.toggle-mute').click(function () {
    const button = $(this);
    const username = button.data('username');
    const isCurrentlyMuted = button.data('is-muted');

    axios.post('/admin', {
        username: username,
        muteStatus: !isCurrentlyMuted  // 发送反转后的状态
    }).then(response => {
        $('.alert').text(response.data.msg).removeClass('d-none');
    });
    button.text(isCurrentlyMuted ? 'Mute' : 'Unmute');  // 更新按钮文本
    button.data('is-muted', !isCurrentlyMuted);  // 更新data-is-muted属性
});