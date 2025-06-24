// notifications.js
function updateNotificationBadge() {
    fetch('/services/notification-count/', { credentials: 'same-origin' })
        .then(response => response.json())
        .then(data => {
            document.querySelectorAll('.notification-badge').forEach(badge => {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            });
        });
}

setInterval(updateNotificationBadge, 10000);
document.addEventListener('DOMContentLoaded', updateNotificationBadge); 