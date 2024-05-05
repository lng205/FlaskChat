$(document).ready(function() {
    $('button').click(function() {
        const username = $(this).closest('div').attr('name');
        const type = $(this).closest('div').find('select').val();
        axios.post('/admin', {
            username: username,
            type: type
        }).then(res => {
            $('.alert').text(res.data.msg).removeClass('d-none');
        })
    })
})