$(document).ready(function() {
    $('button').click(function() {
        const username = $(this).closest('div').attr('name');
        const type = $(this).closest('div').find('select').val();
        axios.post('/admin', {
            username: username,
            type: type
        }).then(res => {
            $('.alert').text(res.data.msg).removeClass('d-none');
        });
    });

    // Attach event handler for toggling mute status
    $('.toggle-mute').click(function() {
        const button = $(this);
        const username = button.data('username');
        const isCurrentlyMuted = button.data('is-muted');

        axios.post('/admin', {
            username: username,
            muteStatus: !isCurrentlyMuted  // 发送反转后的状态
        }).then(response => {
            button.data('is-muted', !isCurrentlyMuted);  // 更新data-is-muted属性
            button.text(isCurrentlyMuted ? 'Mute' : 'Unmute');  // 更新按钮文本
            $('.alert').text(response.data.msg).removeClass('d-none');
        }).catch(error => {
            console.error('Error updating mute status:', error);
        });
    });
});