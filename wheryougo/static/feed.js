// CSRF Token for AJAX requests
    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        console.error('CSRF token not found');
    }
    function toggleLike(postId, event){
        if(event) event.preventDefault();  // prevent form submission

        fetch(`/feed/post/${postId}/like/`, {
            method:'POST',
            headers:{
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        }).then(
            response => response.json()
        ).then(
            data => {
                if(data.success){
                    const likebtn = document.querySelector(`#like-count-${postId}`);
                    likebtn.textContent = data.like_count;
                    const svg = document.querySelector(`#like-icon-${postId}`);
                    if(data.liked){
                    svg.classList.add('text-red-500', 'fill-current');
                    svg.setAttribute('fill', 'currentColor');
                } else {
                    svg.classList.remove('text-red-500', 'fill-current');
                    svg.setAttribute('fill', 'none');
                }
                }
            }
        )
    }
//post/<int:post_id>/favorite/
    function toggleFavorite(postId, event){
        if(event) event.preventDefault();

        fetch(`/feed/post/${postId}/favorite/`, {
            method:'POST',
            headers:{
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        }).then(
            response => response.json()
        ).then(
            data => {
                if(data.success){
                    const favBtn = document.querySelector(`#favourite-count-${postId}`);
                    favBtn.textContent = data.favourite_count;
                    const i = document.querySelector(`#fav-${postId}`);
                    if(data.favourited){
                    i.classList.add('text-red-500', 'fill-current');
                    i.setAttribute('fill', 'currentColor');
                } else {
                    i.classList.remove('text-red-500', 'fill-current');
                    i.setAttribute('fill', 'none');
                }
                }
            }
        )
    }


    // Utility function to get CSRF token from cookies for AJAX POST requests:
    function getCookie(name) {
        let cookieValue = null;
        if(document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for(let i=0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                // Does cookie string begin with name we want?
                if(cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

function loadNotifications(){
    fetch('/notifications/show/')
    .then(response => response.text())
    .then(html => {
        document.getElementById('notifications').innerHTML = html;
    })
    .catch(error => {
        document.getElementById('notifications').innerHTML = '<p class="text-red-500">Failed to load notifications.</p>';
    })    
}
document.addEventListener('DOMContentLoaded', loadNotifications);