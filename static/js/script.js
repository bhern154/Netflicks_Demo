
document.addEventListener("DOMContentLoaded", () => {

    document.getElementById('loading').style.display = 'none';

    // Define a function to set up scrolling for a gallery
    function setupGalleryScroll(leftBtnId, rightBtnId, galleryId) {
        const leftBtn = document.getElementById(leftBtnId);
        const rightBtn = document.getElementById(rightBtnId);
        const gallery = document.getElementById(galleryId);

        if (leftBtn && rightBtn && gallery) {
            // Scroll left
            leftBtn.addEventListener("click", () => {
                gallery.scrollBy({ left: -300, behavior: 'smooth' });
            });

            // Scroll right
            rightBtn.addEventListener("click", () => {
                gallery.scrollBy({ left: 300, behavior: 'smooth' });
            });
        }
    }

    // Set up scrolling for each gallery
    setupGalleryScroll("leftBtn-latest", "rightBtn-latest", "gallery-latest");
    setupGalleryScroll("leftBtn-action", "rightBtn-action", "gallery-action");
    setupGalleryScroll("leftBtn-animation", "rightBtn-animation", "gallery-animation");
    setupGalleryScroll("leftBtn-adventure", "rightBtn-adventure", "gallery-adventure");
    setupGalleryScroll("leftBtn-war", "rightBtn-war", "gallery-war");

    const images = document.querySelectorAll('img.movie-image');
        
        images.forEach(img => {
            img.onerror = function() {
                // Find the closest .image-wrapper and remove it
                const imageWrapper = img.closest('.image-wrapper');
                if (imageWrapper) {
                    imageWrapper.remove();
                }
            };
        });
});


// JavaScript to toggle the search bar visibility
document.getElementById('search-toggle').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default link behavior
    const searchBar = document.getElementById('search-bar');
    if (searchBar.style.display === 'none' || searchBar.style.display === '') {
        searchBar.style.display = 'flex'; // Show the search bar
        searchBar.querySelector('input').focus(); // Focus the input
    } else {
        searchBar.style.display = 'none'; // Hide the search bar
    }
});

// JavaScript to close the search bar when the close button is clicked
document.getElementById('close-search').addEventListener('click', function() {
    const searchBar = document.getElementById('search-bar');
    searchBar.style.display = 'none'; // Hide the search bar
    document.getElementById('search-toggle').focus(); // Return focus to the "Search" link
});



document.addEventListener("DOMContentLoaded", () => {
    const toggles = document.querySelectorAll(".read-more");

    toggles.forEach(toggle => {
        toggle.addEventListener("click", (e) => {
            e.preventDefault(); // Prevent the default link behavior

            const text = toggle.previousElementSibling;

            if (text.classList.contains("expanded")) {
                text.classList.remove("expanded");
                toggle.textContent = "Read More";
            } else {
                text.classList.add("expanded");
                toggle.textContent = "Read Less";
            }
        });
    });
});


// ------------- Function to show the loading screen ----------------
function showLoadingScreen() {
    document.getElementById('loading').style.display = 'block';
}


// ------------- Code for Navbar dropdown menus ----------------

// Function to toggle the visibility of the dropdown
function toggleDropdown(event) {
    // Prevent the default link click behavior
    event.preventDefault();

    // Close any open dropdowns first
    document.querySelectorAll('.dropdown-content').forEach((dropdown) => {
        if (dropdown !== event.target.nextElementSibling) {
            dropdown.classList.remove('show');
        }
    });

    // Toggle the display of the current dropdown
    const dropdownContent = event.target.nextElementSibling;
    if (dropdownContent) {
        dropdownContent.classList.toggle('show');
    }
}

// Close the dropdown if clicked outside of it
function closeDropdownOnClickOutside(event) {
    if (!event.target.matches('.dropdown-toggle')) {
        document.querySelectorAll('.dropdown-content').forEach((dropdown) => {
            dropdown.classList.remove('show');
        });
    }
}

// Attach event listeners
document.querySelectorAll('.dropdown-toggle').forEach((toggle) => {
    toggle.addEventListener('click', toggleDropdown);
});
