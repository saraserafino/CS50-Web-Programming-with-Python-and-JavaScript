document.addEventListener('DOMContentLoaded', function() {
    // Edit post
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postDiv = this.closest('.post');
            const contentDiv = postDiv.querySelector('.content');
            const currentContent = contentDiv.textContent;

            // Replace content with a textarea
            const textarea = document.createElement('textarea');
            textarea.className = 'form-control';
            textarea.value = currentContent;
            contentDiv.innerHTML = '';
            contentDiv.appendChild(textarea);

            // Show save button and hide edit button
            this.style.display = 'none';
            postDiv.querySelector('.save-btn').style.display = 'inline-block';

            // Save button click handler
            postDiv.querySelector('.save-btn').addEventListener('click', function() {
                const newContent = textarea.value;
                const postId = postDiv.dataset.postId;

                // Send AJAX request to save the edit
                fetch(`/edit_post/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken
                    },
                    body: `content=${encodeURIComponent(newContent)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        contentDiv.textContent = data.content;
                        textarea.remove();
                        postDiv.querySelector('.edit-btn').style.display = 'inline-block';
                        this.style.display = 'none';
                    } else {
                        alert('Error saving post: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
            });
        });
    });

    // Like/unlike
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postDiv = this.closest('.post');
            const postId = postDiv.dataset.postId;
            const likeCountSpan = postDiv.querySelector('.like-count');

            fetch(`/toggle_like/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    likeCountSpan.textContent = data.like_count;
                    this.textContent = data.liked ? 'Unlike' : 'Like';
                    this.className = `btn btn-sm ${data.liked ? 'btn-danger' : 'btn-outline-danger'}`;
                    } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        });
    });
});