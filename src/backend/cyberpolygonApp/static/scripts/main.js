
function onScroll() {
    const elements = document.querySelectorAll('.animate');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if (elementPosition < windowHeight - 50) {
        element.classList.add('show');
    }
    });
}

window.addEventListener('scroll', onScroll);
window.onload = onScroll;

document.getElementById('avatarInput').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        document.getElementById('avatarPreview').style.backgroundImage = 'url(' + e.target.result + ')';
      }
      reader.readAsDataURL(file);
    }
  });
