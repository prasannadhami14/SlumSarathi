document.addEventListener('DOMContentLoaded', function () {
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatarPreview');
    if (avatarInput && avatarPreview) {
      avatarInput.addEventListener('change', function(event) {
        const [file] = event.target.files;
        if (file) {
          avatarPreview.src = URL.createObjectURL(file);
        }
      });
    }
  });
  