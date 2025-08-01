/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

// The main function that check if the user is log
document.addEventListener('DOMContentLoaded', () => {
	const loginForm = document.getElementById('login-form');
	const reviewForm = document.getElementById('review-form');
	const token = getCookie('token');
	const placeId = getPlaceIdFromURL();
	console.log("place id: ", placeId);

	if (reviewForm) {
		reviewForm.addEventListener('submit', async (event) => {
			event.preventDefault();
			const newReview = document.getElementById('review').value;
			submitReview(token, placeId, newReview);
		})
	}

	loginForm?.addEventListener('submit', async (event) => {
		event.preventDefault();
		const email = document.getElementById('email').value;
		const password = document.getElementById('password').value;
		await loginUser(email, password);
	});
	checkAuthentication();
});
// price filter
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
// that generated the token
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

// that fetch the user info
async function getCurrentUser(token) {
	try {
		const response = await fetch('http://127.0.0.1:5000/api/v1/users/me', {
			headers: {
				'Authorization': `Bearer ${token}`
			}
		});

		if (response.ok) {
			const user = await response.json();
			return user.id;
		}
	} catch (error) {
		console.error('Erreur lors de la récupération de l\'utilisateur:', error);
	}
	return null;
}
// check if the token is available and display the place on the index page
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
			const placeId = await fetchPlaceDetails(token, urlId);
			displayPlaceDetails([placeId]);
		}
	}
	return token;
}
// fetch the palces informations
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
// fetch the place informations by id
async function fetchPlaceDetails(token, placeId) {
	const response = await fetch("http://127.0.0.1:5000/api/v1/places/" + placeId, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${token}`
		}
	});

	return await response.json();
}
// display dynamically the place info on the page
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

// that split the information of the token
function decodeJWT(token) {
    try {
        const payload = token.split('.')[1];
        const decoded = JSON.parse(atob(payload));
        return decoded;
    } catch (error) {
        console.error('Erreur lors du décodage du JWT:', error);
        return null;
    }
}

// that submit the review 
async function submitReview(token, placeId, reviewText) {
    // Décode the jwt to fetch the user_id
    const decoded = decodeJWT(token);
    const userId = decoded?.sub;
    
    if (!userId) {
        alert('Impossible de récupérer l\'ID utilisateur depuis le token');
        return;
    }
    
    const rating = document.getElementById('rating').value || 5;
    console.log("Rating:", rating);
    
    const bodyData = {
        text: reviewText,
        rating: parseInt(rating),
        user_id: userId,
        place_id: placeId
    };
    console.log("Body envoyé:", bodyData);

    const response = await fetch("http://127.0.0.1:5000/api/v1/reviews", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(bodyData)
    });

    console.log("Response status:", response.status);
    
    // parse the json if possible
    try {
        const responseJson = JSON.parse(responseText);
        console.log("Response JSON:", responseJson);
    } catch (e) {
        console.log("Réponse n'est pas en JSON");
    }

    handleResponse(response);
}
// handle the response if its Ok or not
function handleResponse(response) {
	if (response.ok) {
		showSmashAnimation('success', 'REVIEW SMASHED!', '💥 Avis ajouté avec succès! 💥');
		setTimeout(() => {
			document.getElementById('review-form').reset();
		}, 1500);
	} else {
		showSmashAnimation('fail', 'REVIEW FAILED!', '❌ Échec de l\'envoi! ❌');
	}
}

function displayPlaceDetails(places) {
	const sectionPlace = document.getElementById("place-details");
	const sectionReview = document.getElementById("reviews");
	const cards = places.map(place => {
		const amenitiesList = place.amenities
			.map(amenity => `<li>${amenity.name}</li>`)
			.join('');
		return `
		<div class="place-details">
			<h1 class="title-place">${place.title}</h1>
			<div class="place-info">
				<p><strong>Hote :</strong> ${place.owner.first_name}</p>
				<p><strong>Prix :</strong> ${place.price}€ par nuit</p>
				<p><strong>Description :</strong> ${place.description}</p>
				<p><strong>Equipements :</strong></p>
				<br>
				<ul>
					${amenitiesList}
				</ul>
			</div>
		</div>
		`;
	});
	sectionPlace.innerHTML = cards.join('');
	const cardReview = places.map(place => {
		const reviewList = Array.isArray(place.reviews)
			? place.reviews.map(review => `<p>Comment :</strong> ${review.text}</p>
						<p><strong>User name :</strong> ${review.user_firstName} ${review.user_lastName}</p>
						<p><strong>Rating :</strong> ${review.rating}</p>`)
				.join('')
			: '<p>Aucun avis pour ce lieu.</p>';
		return `
	<h2>commentaire des lieux</h2>
    <!-- Reviews will be populated dynamically -->
	<div class="review-card">
		${reviewList}
	</div>
		<button class="add-review" onclick="window.location.href='add_review.html?id=${place.id}'" id="add-review-btn">Ajouter un avis</button>
	`;
	})
	sectionReview.innerHTML = cardReview.join('');
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
// that get the url id
function getPlaceIdFromURL() {
	const response = new URLSearchParams(window.location.search);
	return response.get('id');
}


/* =========================================================================== */

// Fonction pour afficher les animations Super Smash
function showSmashAnimation(type, title, message) {
	// Créer l'overlay
	const overlay = document.createElement('div');
	overlay.className = 'smash-overlay';

	// Créer le contenu de l'animation
	const animationContent = document.createElement('div');
	animationContent.className = type === 'success' ? 'smash-success' : 'smash-fail';

	animationContent.innerHTML = `
        <div>${title}</div>
        <div style="font-size: 1.2rem; margin-top: 1rem;">${message}</div>
    `;

	overlay.appendChild(animationContent);
	document.body.appendChild(overlay);

	// Ajouter des particules pour le succès
	if (type === 'success') {
		createParticles(overlay);
	}

	// Afficher l'animation
	setTimeout(() => {
		overlay.classList.add('show');
	}, 10);

	// Masquer l'animation après 2.5 secondes
	setTimeout(() => {
		overlay.classList.remove('show');
		setTimeout(() => {
			document.body.removeChild(overlay);
		}, 300);
	}, 2500);
}

// Fonction pour créer des particules (effet visuel)
function createParticles(container) {
	for (let i = 0; i < 20; i++) {
		setTimeout(() => {
			const particle = document.createElement('div');
			particle.className = 'smash-particles';
			particle.style.left = Math.random() * 100 + '%';
			particle.style.top = Math.random() * 100 + '%';
			particle.style.background = Math.random() > 0.5 ? '#ffcc00' : '#ff003c';
			container.appendChild(particle);

			// Supprimer la particule après l'animation
			setTimeout(() => {
				if (container.contains(particle)) {
					container.removeChild(particle);
				}
			}, 1000);
		}, i * 50);
	}
}
