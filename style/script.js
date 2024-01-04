const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
    updateBrowserTitle("Create Account");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
    updateBrowserTitle("Login");
});
function updateBrowserTitle(title) {
    document.title = title;
}