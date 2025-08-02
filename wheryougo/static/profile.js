
    function showPosts() {
        switchTab('posts');
    }
    function toggleTheme() {
                const html = document.documentElement;
                const sunIcon = document.getElementById('sun-icon');
                const moonIcon = document.getElementById('moon-icon');
                const mobileThemeText = document.getElementById('mobile-theme-text');
                
                if (html.classList.contains('dark')) {
                    // Switch to light mode
                    html.classList.remove('dark');
                    localStorage.setItem('theme', 'light');
                    
                    // Update icons
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                    
                    // Update mobile text
                    if (mobileThemeText) {
                        mobileThemeText.textContent = 'Dark Mode';
                    }
                } else {
                    // Switch to dark mode
                    html.classList.add('dark');
                    localStorage.setItem('theme', 'dark');
                    
                    // Update icons
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                    
                    // Update mobile text
                    if (mobileThemeText) {
                        mobileThemeText.textContent = 'Light Mode';
                    }
                }
            }

            // Initialize theme on page load
            function initializeTheme() {
                const savedTheme = localStorage.getItem('theme');
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const html = document.documentElement;
                const sunIcon = document.getElementById('sun-icon');
                const moonIcon = document.getElementById('moon-icon');
                const mobileThemeText = document.getElementById('mobile-theme-text');
                
                if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
                    html.classList.add('dark');
                    sunIcon.classList.add('hidden');
                    moonIcon.classList.remove('hidden');
                    if (mobileThemeText) {
                        mobileThemeText.textContent = 'Light Mode';
                    }
                } else {
                    html.classList.remove('dark');
                    sunIcon.classList.remove('hidden');
                    moonIcon.classList.add('hidden');
                    if (mobileThemeText) {
                        mobileThemeText.textContent = 'Dark Mode';
                    }
                }
            }

            // Initialize theme when DOM is loaded
            document.addEventListener('DOMContentLoaded', initializeTheme);
            
            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    initializeTheme();
                }
            });
    function showFavorites(userId) {
        switchTab('favorites');
        const favoritesContent = document.getElementById('favorites-content');
        if (!favoritesContent.dataset.loaded) {
            fetch(`/profile/favourites/${userId}/`)
                .then(response => response.text())
                .then(html => {
                    favoritesContent.innerHTML = html;
                    favoritesContent.dataset.loaded = "true";
                })
                .catch(error => {
                    favoritesContent.innerHTML = "<div class='text-red-500'>Failed to load favorites.</div>";
                });
        }
    }

    function showAbout() {
        switchTab('about');
    }

    function switchTab(tabName) {
        // Hide all content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.tab-btn').forEach(tab => {
            tab.classList.remove('active', 'border-travel-blue', 'text-travel-blue');
            tab.classList.add('border-transparent', 'text-gray-500');
        });
        
        // Show selected content
        document.getElementById(tabName + '-content').classList.remove('hidden');
        
        // Activate selected tab
        const activeTab = document.getElementById(tabName + '-tab');
        activeTab.classList.add('active', 'border-travel-blue', 'text-travel-blue');
        activeTab.classList.remove('border-transparent', 'text-gray-500');
    }

    // Follow user
    function followUser(username) {
        fetch(`/profile/ajax/follow/${username}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const btn = document.getElementById('follow-btn');
                const followersCount = document.getElementById('followers-count');
                
                if (data.following) {
                    btn.innerHTML = `
                        <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        Following
                    `;
                    btn.className = 'bg-gray-100 text-gray-700 hover:bg-gray-200 px-6 py-2 rounded-lg font-medium transition duration-200';
                } else {
                    btn.innerHTML = `
                        <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                        Follow
                    `;
                    btn.className = 'bg-travel-blue text-white hover:bg-blue-700 px-6 py-2 rounded-lg font-medium transition duration-200';
                }
                
                followersCount.textContent = data.followers_count;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Edit profile
    function editProfile() {
        document.getElementById('edit-profile-modal').classList.remove('hidden');
    }

    function closeEditProfile() {
        document.getElementById('edit-profile-modal').classList.add('hidden');
    }

    // Profile picture upload
    function uploadProfilePic(input) {
        if (input.files && input.files[0]) {
            const formData = new FormData();
            formData.append('pfp', input.files[0]);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            
            // You can implement AJAX upload here
            console.log('Profile picture upload triggered');
        }
    }

    // Handle edit profile form submission
    document.getElementById('edit-profile-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        fetch(window.location.href + 'edit/', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });