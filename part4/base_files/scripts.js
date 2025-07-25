/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', () => {
	/* DO SOMETHING */
	const loginForm = document.getElementById('login-form');

	loginForm?.addEventListener('submit', async (event) => {
		event.preventDefault();
		const email = document.getElementById('email').value;
		const password = document.getElementById('password').value;
		await loginUser(email, password);
	});

	checkAuthentication();
});

async function loginUser(email, password) {
	const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ email, password })
	});

	if (!response.ok) {
		alert('Login failed: ' + response.statusText);
		return;
	}

	const data = await response.json();
	document.cookie = `token=${data.access_token}; path=/`;
	window.location.href = 'index.html';
}

function checkAuthentication() {
	const token = getCookie('token');
	const loginLink = document.getElementById('login-link');

	if (!token) {
		loginLink.style.display = 'block';
	} else {
		loginLink.style.display = 'none';
		// Fetch places data if the user is authenticated
		fetchPlaces(token);
	}
}

async function fetchPlaces(token) {
	const response = await fetch('http://127.0.0.1:5000/api/v1/places', {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${token}`,
		}
	});

	if (!response.ok) {
		alert('Failed to fetch places: ' + response.statusText);
		return;
	}

	const places = await response.json();

	console.log('Places data:', places);
}

// Function to get a cookie value by its name
function getCookie(name) {

	const cookie = document.cookie.split(';').find(row => row.startsWith(name + '='));

	if (!cookie) {
		return null;
	}

	const cookieParts = cookie.split('=');
	const value = cookieParts[1];
	return value;
}