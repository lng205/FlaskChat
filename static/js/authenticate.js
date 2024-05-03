$('form').submit(function(event) {
    // The form would send a GET request by default
    event.preventDefault();
    axios.post(
        $(this).attr('action'),
        new FormData(this)
    ).then(res => {
        if (res.data.error) {
            $('.alert').text(res.data.error).removeClass('d-none');
        }
        else {
            Cookies.set('auth_token', res.data.token, { secure: true, sameSite: 'strict' });
            Cookies.set('username', res.data.username, { secure: true, sameSite: 'strict' });
            window.location.href = res.data.redirect;
        }
    })
})