const username = cookies.get('username');
$('#postSubmitButton').click(function() {
    const text = $('#postText').val();
    axios.post('/post', {
        username: username,
        text: text
    })
});