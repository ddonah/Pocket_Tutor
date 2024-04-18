// function to sign users up
function signup() {
    var formData = new FormData(document.getElementById("signupForm"));
    var object = {};
    formData.forEach(function(value, key){
        object[key] = value;
    });
    var json = JSON.stringify(object);
    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: json
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Signed up successfully!');
            displayQuiz();
        } else {
            alert('Signup failed: ' + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


// function to log users in
function login() {
    var loginEmail = document.getElementById("loginEmail").value;
    var loginPass = document.getElementById("loginPass").value;

    var json = JSON.stringify({
        email: loginEmail,
        password: loginPass
    });
    console.log("Login request JSON:", json);
    fetch('/user_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: json
    })
    .then(response => response.json())
    .then(data => {
        console.log("Login response:", data); 
        if (data.success) {
            alert('Logged in successfully!');
            displayQuiz();
        } else {
            alert('Login failed: ' + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// displays quiz page when called
function displayQuiz() {
    window.location.href = "/quiz";
}

// displays the question
function displayQuestion(index) {
    document.getElementById("question").innerText = questions[index];
}
