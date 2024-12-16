function onScroll(): void {
    const elements = document.querySelectorAll('.animate');
    
    elements.forEach((element) => {
        const elementPosition = (element as HTMLElement).getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if (elementPosition < windowHeight - 50) {
            element.classList.add('show');
        }
    });
}

window.addEventListener('scroll', onScroll);
window.onload = onScroll;

document.getElementById('avatarInput')?.addEventListener('change', function (this: HTMLInputElement) {
    const file = this.files?.[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e: ProgressEvent<FileReader>) {
            const avatarPreview = document.getElementById('avatarPreview') as HTMLElement;
            if (avatarPreview && e.target) {
                avatarPreview.style.backgroundImage = `url(${e.target.result})`;
            }
        };
        reader.readAsDataURL(file);
    }
});
