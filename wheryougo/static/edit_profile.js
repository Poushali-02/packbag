
// Image preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('profile-preview');
            if (preview.tagName === 'IMG') {
                preview.src = e.target.result;
            } else {
                // Replace the div with an img
                const img = document.createElement('img');
                img.id = 'profile-preview';
                img.src = e.target.result;
                img.alt = '{{ user_profile.name }}';
                img.className = 'w-24 h-24 sm:w-32 sm:h-32 rounded-full object-cover border-4 border-white shadow-lg';
                preview.parentNode.replaceChild(img, preview);
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Bio character counter
document.getElementById('bio').addEventListener('input', function() {
    const bioCount = document.getElementById('bio-count');
    const length = this.value.length;
    bioCount.textContent = length + '/500';
    
    if (length > 500) {
        bioCount.classList.add('text-red-500');
        bioCount.classList.remove('text-gray-400');
    } else {
        bioCount.classList.remove('text-red-500');
        bioCount.classList.add('text-gray-400');
    }
});

// Delete account modal
function confirmDelete() {
    document.getElementById('delete-modal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('delete-modal').classList.add('hidden');
}

function deleteAccount() {
    // Implement delete account functionality
    alert('Delete account functionality would be implemented here');
    closeDeleteModal();
}
