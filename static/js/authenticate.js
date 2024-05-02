$('#login_button').click(() => authenticate('/login/user'));
$('#signup_button').click(() => authenticate('/signup/user'));

async function authenticate(url) {
    let res = await axios.post(url, {
        username: $("#username").val(),
        password: $("#password").val()
    });
    if (res.data[0] != "/") {
        alert(res.data);
        return;
    }
    Cookies.set("username", $("#username").val());
    window.open(res.data, "_self")
}