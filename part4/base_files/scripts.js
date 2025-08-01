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

if (document.getElementById('price-filter')) {
	document.getElementById('price-filter').addEventListener('change', (event) => {
		const selectedPrice = event.target.value;
		if (selectedPrice === 'all') {
			displayPlaces(window.allPlaces)
		} else {
			displayPlaces(window.allPlaces.filter(place => place.price <= parseInt(selectedPrice)));
		}
	});
}

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

async function checkAuthentication() {
	const token = getCookie('token');
	const loginLink = document.getElementById('login-link');
	const addReviewSection = document.getElementById('add-review-btn');

	if (loginLink) {
		if (!token) {
			loginLink.style.display = 'block';
		} else {
			loginLink.style.display = 'none';
			// Fetch places data if the user is authenticated
			const places = await fetchPlaces(token);
			displayPlaces(places);
		}
	}

	if (addReviewSection) {
		if (!token) {
			addReviewSection.style.display = 'block';
		} else {
			addReviewSection.style.display = 'none';
			urlId = getPlaceIdFromURL();
			console.log("urlId: ", urlId);
			const placeId = await fetchPlaceDetails(token, urlId);
			console.log("placeId: ", placeId);
			displayPlaceDetails([placeId]);
		}
	}
}

async function fetchPlaces(token) {
	const response = await fetch('http://127.0.0.1:5000/api/v1/places', {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
		}
	});

	if (!response.ok) {
		alert('Failed to fetch places: ' + response.statusText);
		return;
	}

	const places = await response.json();

	const promises = places.map(place => fetch("http://127.0.0.1:5000/api/v1/places/" + place.id));
	const promises_array = await Promise.all(promises);
	const promise_json = await promises_array.map(promise_array => promise_array.json());
	const results = await Promise.all(promise_json);
	window.allPlaces = results;
	window.PlaceId = results;

	return results;
}

async function fetchPlaceDetails(token, placeId) {
	const response = await fetch("http://127.0.0.1:5000/api/v1/places/" + placeId, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': token
		}
	});

	return await response.json();
}

async function displayPlaces(places) {
	if (document.getElementById('places-list')) {
		const section = document.getElementById("places-list");
		const cards = places.map(place => `
		<div class="place-card">
			<h2>${place.title}</h2>
			<span>Prix : ${place.price}€</span>
			<button class="details-button" onclick="window.location.href ='place.html?id=${place.id}'">View Details</button>
		</div>
	`);
		section.innerHTML = cards.join('');
	}
}

function displayPlaceDetails(places) {
	const section = document.getElementById("place-details");
	const amenity = places.map(place => place.amenity);
	console.log("amenity : ", amenity);
	const cards = places.map(place => `
		<div class="place-details">
			<h1 class="title-place">${place.title}</h1>
			<div class="place-info">
				<p><strong>Hote :</strong> ${place.owner.first_name}</p>
				<p><strong>Prix :</strong> ${place.price}€ par nuit</p>
				<p><strong>Description :</strong> ${place.description}</p>
				<p><strong>Equipements :</strong></p>
				<br>
				<ul>
					<li>Wi-fi</li>
					<li>Climatisation</li>
					<li>Parking</li>
					<li>Animaux acceptes</li>
				</ul>
			</div>
		</div>
	`);
	section.innerHTML = cards.join('');
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

function getPlaceIdFromURL() {
	const response = new URLSearchParams(window.location.search);
	return response.get('id');
}