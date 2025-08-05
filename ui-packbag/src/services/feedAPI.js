// API service for communicating with Django backend
const API_BASE_URL = 'http://127.0.0.1:8000';

class FeedAPI {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Helper method to make API calls
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session auth
    };

    const config = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Get feed posts
  async getFeed(page = 1) {
    return this.makeRequest(`/feed/api/feed/?page=${page}`);
  }

  // Create a new post
  async createPost(postData, images = []) {
    const formData = new FormData();
    
    // Add post data
    Object.keys(postData).forEach(key => {
      formData.append(key, postData[key]);
    });
    
    // Add images
    images.forEach((image, index) => {
      formData.append('images', image.file);
      formData.append('image_captions', image.caption || '');
    });

    return this.makeRequest('/feed/api/posts/create/', {
      method: 'POST',
      headers: {}, // Don't set Content-Type for FormData
      body: formData,
    });
  }

  // Get single post
  async getPost(postId) {
    return this.makeRequest(`/feed/api/posts/${postId}/`);
  }

  // Toggle like on post
  async toggleLike(postId) {
    return this.makeRequest(`/feed/api/posts/${postId}/like/`, {
      method: 'POST',
    });
  }

  // Toggle favorite on post
  async toggleFavorite(postId) {
    return this.makeRequest(`/feed/api/posts/${postId}/favorite/`, {
      method: 'POST',
    });
  }

  // Add comment to post
  async addComment(postId, content, parentId = null) {
    return this.makeRequest(`/feed/api/posts/${postId}/comment/`, {
      method: 'POST',
      body: JSON.stringify({
        content,
        parent_id: parentId,
      }),
    });
  }

  // Toggle like on comment
  async toggleCommentLike(commentId) {
    return this.makeRequest(`/feed/api/comments/${commentId}/like/`, {
      method: 'POST',
    });
  }

  // Get tag suggestions
  async getTagSuggestions(query = '') {
    return this.makeRequest(`/feed/api/tags/suggestions/?q=${encodeURIComponent(query)}`);
  }

  // Search posts
  async searchPosts(query, filters = {}) {
    const params = new URLSearchParams({
      q: query,
      ...filters,
    });
    return this.makeRequest(`/feed/api/posts/search/?${params}`);
  }

  // Get user posts
  async getUserPosts(userId = null, page = 1) {
    const endpoint = userId 
      ? `/feed/api/users/${userId}/posts/?page=${page}`
      : `/feed/api/users/posts/?page=${page}`;
    return this.makeRequest(endpoint);
  }
}

export default new FeedAPI();
