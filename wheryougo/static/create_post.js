
        // Character counters
        document.getElementById('title').addEventListener('input', function() {
            const count = this.value.length;
            document.getElementById('title-count').textContent = count + '/200';
            
            if (count > 200) {
                document.getElementById('title-count').classList.add('text-red-500');
            } else {
                document.getElementById('title-count').classList.remove('text-red-500');
            }
        });

        document.getElementById('content').addEventListener('input', function() {
            const count = this.value.length;
            document.getElementById('content-count').textContent = count + ' characters';
        });

        // Post type selection
        document.querySelectorAll('input[name="post_type"]').forEach(radio => {
            radio.addEventListener('change', function() {
                // Remove selected class from all cards
                document.querySelectorAll('.post-type-card').forEach(card => {
                    card.classList.remove('border-travel-blue', 'bg-blue-50');
                    card.classList.add('border-gray-200');
                });
                
                // Add selected class to chosen card
                if (this.checked) {
                    const card = this.parentNode.querySelector('.post-type-card');
                    card.classList.remove('border-gray-200');
                    card.classList.add('border-travel-blue', 'bg-blue-50');
                }
            });
        });

        // Initialize first post type as selected
        document.querySelector('input[name="post_type"]:checked').dispatchEvent(new Event('change'));

        // Image upload handling
        let uploadedImages = [];

        // Update the handleImageUpload function
        function handleImageUpload(files) {
            Array.from(files).forEach(file => {
                if (!file.type.startsWith('image/')) {
                    showError('Please select only image files.');
                    return;
                }
                
                if (file.size > 10 * 1024 * 1024) {
                    showError('Image must be smaller than 10MB.');
                    return;
                }
                
                if (uploadedImages.length >= 5) {
                    showError('Maximum 5 images allowed.');
                    return;
                }
                
                // Store the actual file object
                uploadedImages.push(file);
                
                // Add preview to UI
                addImagePreview(file);
            });
        }

        function addImagePreview(file) {
            const container = document.getElementById('image-previews');
            const imageIndex = uploadedImages.length - 1;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'relative bg-gray-100 rounded-lg overflow-hidden';
                previewDiv.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" class="w-full h-32 object-cover">
                    <button type="button" onclick="removeImage(${imageIndex})" class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600">
                        ×
                    </button>
                    <div class="p-2">
                        <input type="text" name="image_captions[]" placeholder="Add a caption..." 
                            class="w-full text-sm border border-gray-300 rounded px-2 py-1">
                    </div>
                `;
                container.appendChild(previewDiv);
            };
            reader.readAsDataURL(file);
            
            updateImageCount();
        }

        // Remove image function
        function removeImage(index) {
            uploadedImages.splice(index, 1);
            
            // Rebuild the preview container
            const container = document.getElementById('image-previews');
            container.innerHTML = '';
            
            // Re-add all remaining images
            uploadedImages.forEach((file, newIndex) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'relative bg-gray-100 rounded-lg overflow-hidden';
                    previewDiv.innerHTML = `
                        <img src="${e.target.result}" alt="Preview" class="w-full h-32 object-cover">
                        <button type="button" onclick="removeImage(${newIndex})" class="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600">
                            ×
                        </button>
                        <div class="p-2">
                            <input type="text" name="image_captions[]" placeholder="Add a caption..." 
                                class="w-full text-sm border border-gray-300 rounded px-2 py-1">
                        </div>
                    `;
                    container.appendChild(previewDiv);
                };
                reader.readAsDataURL(file);
            });
            
            updateImageCount();
        }
        // IMPORTANT: Update form submission to include files
        document.getElementById('create-post-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Create FormData object
            const formData = new FormData();
            
            // Add CSRF token
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            
            // Add form fields
            formData.append('post_type', document.querySelector('input[name="post_type"]:checked')?.value || 'travel');
            formData.append('title', document.getElementById('title').value);
            formData.append('content', document.getElementById('content').value);
            formData.append('location', document.getElementById('location').value);
            formData.append('tags', document.getElementById('tags').value);
            formData.append('privacy', document.querySelector('input[name="privacy"]:checked')?.value || 'public');
            
            // Collect categories
            const selectedCategories = [];
            document.querySelectorAll('input[name="categories"]:checked').forEach(checkbox => {
                selectedCategories.push(checkbox.value);
            });
            formData.append('categories', selectedCategories.join(','));
            
            // CRITICAL: Add uploaded images to FormData
            uploadedImages.forEach((file, index) => {
                formData.append('uploaded_images', file);
            });
            
            // Add image captions
            const captions = document.querySelectorAll('input[name="image_captions[]"]');
            captions.forEach(caption => {
                formData.append('image_captions[]', caption.value);
            });
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Sharing...';
            
            // Submit with fetch
            fetch(this.action || window.location.href, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = response.url || '/profile/{{ user.username }}/';
                } else {
                    throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error creating post. Please try again.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });

        // Upload area click handler
        document.getElementById('upload-area').addEventListener('click', function() {
            document.getElementById('images').click();
        });

        // Drag and drop
        const uploadArea = document.getElementById('upload-area');

        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('border-travel-blue', 'bg-blue-50');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('border-travel-blue', 'bg-blue-50');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('border-travel-blue', 'bg-blue-50');
            
            const files = Array.from(e.dataTransfer.files);
            const imageInput = document.getElementById('images');
            
            // Create a new FileList
            const dt = new DataTransfer();
            files.forEach(file => dt.items.add(file));
            imageInput.files = dt.files;
            
            handleImageUpload(imageInput);
        });

        // Tag suggestions
        function addTag(tag) {
            const tagsInput = document.getElementById('tags');
            const currentTags = tagsInput.value.split(',').map(t => t.trim()).filter(t => t);
            
            if (!currentTags.includes(tag)) {
                if (currentTags.length > 0) {
                    tagsInput.value = currentTags.join(', ') + ', ' + tag;
                } else {
                    tagsInput.value = tag;
                }
            }
        }

        // Form submission
        document.getElementById('create-post-form').addEventListener('submit', function(e) {
            // Validate required fields
            const title = document.getElementById('title').value.trim();
            const content = document.getElementById('content').value.trim();
            
            if (!title) {
                e.preventDefault();
                alert('Please add a title to your post.');
                document.getElementById('title').focus();
                return;
            }
            
            if (!content && uploadedImages.length === 0) {
                e.preventDefault();
                alert('Please add some content or images to your post.');
                document.getElementById('content').focus();
                return;
            }
            
            // Prepare form data for submission
            const formData = new FormData(this);
            
            // Add uploaded images
            uploadedImages.forEach((file, index) => {
                formData.append('uploaded_images', file);
            });
            
            // Collect categories
            const selectedCategories = [];
            document.querySelectorAll('input[name="categories"]:checked').forEach(checkbox => {
                selectedCategories.push(checkbox.value);
            });
            formData.set('categories', selectedCategories.join(','));
            
            // Set privacy
            const privacy = document.querySelector('input[name="privacy"]:checked').value;
            formData.set('is_private', privacy === 'private' ? 'true' : 'false');
        });
    