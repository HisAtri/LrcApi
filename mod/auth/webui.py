def html_login():
    html = r"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <title>LyricsAPI</title>
        <link rel="stylesheet" href="/src/css/mod.css">
        <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.css">
        <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            form {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }
        </style>
    </head>
    <body>
        <form id="loginForm" class="form-inline" onsubmit="return false;">
            <div class="form-group mx-sm-3 mb-2">
                <label for="inputPassword" class="sr-only">Auth Key</label>
                <input type="password" class="form-control" id="inputPassword" placeholder="Password" onkeyup="handleKeyPress(event)">
            </div>
            <button type="button" class="btn btn-primary mb-2" onclick="submitLoginForm()">登录</button>
        </form>
        <div class="alert alert-danger" role="alert" id="failed" style="display:none">
            登录失败，请检查您的认证信息。
        </div>
    </body>
    <script>
        function submitLoginForm() {
            var password = document.getElementById("inputPassword").value;
            fetch('/login-api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to the homepage on successful login
                    window.location.href = '/';
                } else {
                    // Show the failed alert
                    document.getElementById("failed").style.display = "block";
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
        function handleKeyPress(event) {
            if (event.keyCode === 13) {
                submitLoginForm();
            }
        }
    </script>
    """
    return html


def error():
    html_error = r"""
    <!doctype html>
    <html lang=en>
    <title>403 Forbidden</title>
    <h1>Forbidden</h1>
    <p>You don't have the permission to access the requested resource.</p>
    <p>Maybe you're not logged in with legitimate credentials, or the cookie has expired</p>
    <p>You will be redirected to the <a href="/login">login page</a> within 3 seconds</p>
    <script>
        setTimeout(function() {
            window.location.href = "/login";
        }, 3000);
    </script>
    """
    return html_error
