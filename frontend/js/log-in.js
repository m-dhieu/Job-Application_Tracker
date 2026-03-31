// Log in page script

// Wait until the DOM content is fully loaded before running the script
document.addEventListener('DOMContentLoaded', function() {
  // Get references to the login and signup forms and their toggle buttons
  var loginForm = document.getElementById('login-form');
  var signupForm = document.getElementById('signup-form');
  var loginToggle = document.getElementById('login-toggle');
  var signupToggle = document.getElementById('signup-toggle');

  // Add click event listener to toggle to login form
  loginToggle.addEventListener('click', function() {
    // Show login form and hide signup form
    loginForm.classList.add('active');
    signupForm.classList.remove('active');

    // Highlight login toggle and unhighlight signup toggle
    loginToggle.classList.add('active');
    signupToggle.classList.remove('active');
  });

  // Add click event listener to toggle to signup form
  signupToggle.addEventListener('click', function() {
    // Show signup form and hide login form
    signupForm.classList.add('active');
    loginForm.classList.remove('active');

    // Highlight signup toggle and unhighlight login toggle
    signupToggle.classList.add('active');
    loginToggle.classList.remove('active');
  });

  // Handle login form submission
  loginForm.addEventListener('submit', function(event) {
    event.preventDefault();

    var emailInput = document.getElementById('login-email');
    var passwordInput = document.getElementById('login-password');
    var email = emailInput.value.trim();
    var password = passwordInput.value.trim();

    // Validate both email and password are provided
    if (!email || !password) {
      alert('Please enter both email and password.');
      if (!email) {
        emailInput.focus();
      } else {
        passwordInput.focus();
      }
      return;
    }

    // Log login information 
    console.log('Logging in with:', email, password);

    // Redirect to dashboard page 
    window.location.href = '/dashboard';
  });

  // Handle signup form submission
  signupForm.addEventListener('submit', function(event) {
    event.preventDefault();

    var usernameInput = document.getElementById('signup-username');
    var emailInput = document.getElementById('signup-email');
    var passwordInput = document.getElementById('signup-password');
    var username = usernameInput.value.trim();
    var email = emailInput.value.trim();
    var password = passwordInput.value.trim();

    // Validate filling all fields 
    if (!username || !email || !password) {
      alert('Please fill out all signup fields.');
      if (!username) {
        usernameInput.focus();
      } else if (!email) {
        emailInput.focus();
      } else {
        passwordInput.focus();
      }
      return;
    }

    // Log signup information 
    console.log('Signing up with:', username, email, password);

    // Notify user of successful signup
    alert('Signup successful! Please proceed to login.');

    // Reset signup form fields
    signupForm.reset();

    // Switch to login form after signup
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
    loginToggle.classList.add('active');
    signupToggle.classList.remove('active');
  });
});
