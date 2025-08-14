// Initialize map
const map = L.map('map').setView([45.160, -87.200], 13); // Adjust center/zoom as needed
const mapLayers = {}; 

// Add basemap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Icon definitions
const icons = {
  campsite: L.icon({
    iconUrl: '/static/icons/campsite.png',
    iconSize: [25, 25],
    iconAnchor: [12, 25],
    popupAnchor: [0, -25]
  }),
  parking: L.icon({
    iconUrl: '/static/icons/parking.png',
    iconSize: [25, 25],
    iconAnchor: [12, 25],
    popupAnchor: [0, -25]
  }),
  trailhead: L.icon({
    iconUrl: '/static/icons/trailhead.png',
    iconSize: [25, 25],
    iconAnchor: [12, 25],
    popupAnchor: [0, -25]
  }),
  winery: L.icon({
    iconUrl: '/static/icons/winery.png',
    iconSize: [25, 25],
    iconAnchor: [12, 25],
    popupAnchor: [0, -25]
  })
};




// Popup formatting functions
const popupFormatters = {
  campsite: props => {
    const desc = props.popup_desc || 'No description available';
    const bookingLink = props.website_url
      ? `<a href="${props.website_url}" target="_blank" rel="noopener noreferrer">Book this campsite</a>`
      : 'Booking link not available';
    const amenities = props.amenities || 'Not listed';
    const siteType = props.site_type || 'Unknown';

    return `
      <strong>${props.site_name || 'Campsite'}</strong><br>
      <em>${desc}</em><br>
      <strong>Type:</strong> ${siteType}<br>
      <strong>Amenities:</strong> ${amenities}<br>
      ${bookingLink}
    `;
  },

  parking: props => `
    <strong>${props.name || 'Parking Area'}</strong>
  `,

  trailhead: props => {
    const name = props.trail_name || 'Trailhead';
    const desc = props.description || 'No description available';
    const difficulty = props.difficulty || 'Unknown';
    const length = props.length ? `${props.length} miles` : 'Length not listed';

    return `
      <strong>${name}</strong><br>
      <em>${desc}</em><br>
      <strong>Difficulty:</strong> ${difficulty}<br>
      <strong>Length:</strong> ${length}
    `;
  },

  winery: props => {
    const name = props.name || 'Winery';
    const address = props.address || 'Address not listed';
    const website = props.website_url
      ? `<a href="${props.website_url}" target="_blank" rel="noopener noreferrer">Visit Website</a>`
      : 'Website not available';

    return `
      <strong>${name}</strong><br>
      <strong>Address:</strong> ${address}<br>
      ${website}
    `;
  }
}; 



// Layer loader function
function loadLayer(url, iconType, layerName, popupFn) {
  fetch(url)
    .then(res => res.json())
    .then(data => {
      const layer = L.geoJSON(data, {
        pointToLayer: (feature, latlng) => L.marker(latlng, { icon: icons[iconType] }),
        onEachFeature: (feature, layer) => {
          const props = feature.properties;
          const popupContent = popupFn ? popupFn(props) : `<strong>${props.name || layerName}</strong>`;
          layer.bindPopup(popupContent);
        }
      }).addTo(map);

      mapLayers[layerName] = layer; // Save reference for toggling
    })
    .catch(err => console.error(`Error loading ${layerName}:`, err));
}

// Load all layers
loadLayer('http://127.0.0.1:5000/api/campsites', 'campsite', 'Campsites', popupFormatters.campsite);
loadLayer('http://127.0.0.1:5000/api/parking', 'parking', 'Parking', popupFormatters.parking);
loadLayer('http://127.0.0.1:5000/api/trailheads', 'trailhead', 'Trailheads', popupFormatters.trailhead);
loadLayer('http://127.0.0.1:5000/api/wineries', 'winery', 'Wineries', popupFormatters.winery);



function toggleLayer(name) {
  const layer = mapLayers[name];
  if (!layer) return;

  if (map.hasLayer(layer)) {
    map.removeLayer(layer);
  } else {
    map.addLayer(layer);
  }
}

function showUserLocation() {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(position => {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;

    const userMarker = L.marker([lat, lng]).addTo(map);

    userMarker.bindPopup("You are here").openPopup();
    map.setView([lat, lng], 15);
  }, () => {
    alert("Unable to retrieve your location.");
  });
}

// Capture map click to autofill location
map.on('click', function(e) {
  const latlng = `${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}`;
  document.getElementById('location').value = latlng;
});

// Submit form to Flask
document.getElementById('sighting-form').addEventListener('submit', function(e) {
  e.preventDefault();
  const species = document.getElementById('species').value;
  const location = document.getElementById('location').value;
  const notes = document.getElementById('notes').value;

  fetch('/submit_sighting', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ species, location, notes })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const [lat, lng] = location.split(',').map(Number);
      const marker = L.marker([lat, lng]).addTo(map);
      marker.bindPopup(`<strong>${species}</strong><br>${notes || 'No notes'}`).openPopup();
      document.getElementById('sighting-form').reset();
      document.getElementById('location').value = '';
    }
  });
});