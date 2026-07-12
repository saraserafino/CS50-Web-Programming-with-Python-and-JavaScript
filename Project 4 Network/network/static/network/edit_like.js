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

            // Hide edit button and show save button
            this.style.display = 'none';
            postDiv.querySelector('.save-btn').style.display = 'inline-block';

            // Save
            postDiv.querySelector('.save-btn').addEventListener('click', function() {
                const newContent = textarea.value;
                const postId = postDiv.dataset.postId;

                // Send AJAX request to save
                fetch(`/edit_post/${postId}`, {
                    method: 'POST',
                    headers: {
// With this attribute, form data is encoded into a string of key-value pairs where key-value pairs are separated by & and keys and values are separated by = (ex. name=Sara&age=27)
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
            const isLiked = this.classList.contains('text-danger');

            fetch(`/like/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(`action=${isLiked ? 'unlike' : 'like'}`)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update like count
                    likeCountSpan.textContent = data.like_count;
                    // Update button icon and state
                    if (data.liked) {
                        this.innerHTML = '<span style="color:red">&#9829;</span>';
                        this.classList.add('text-danger');
                        this.classList.remove('text-outline-danger');
                        this.dataset.liked = 'true';
                    } else {
                        this.innerHTML = '&#9825;';
                        this.classList.add('text-outline-danger');
                        this.classList.remove('text-danger');
                        this.dataset.liked = 'false';
                    }
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