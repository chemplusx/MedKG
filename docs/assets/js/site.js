document.addEventListener('DOMContentLoaded', () => {
    const mobileToggle = document.querySelector('[data-nav-toggle]');
    const mobileMenu = document.querySelector('[data-mobile-nav]');

    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', event => {
            const targetId = anchor.getAttribute('href');
            if (targetId.length > 1) {
                const target = document.querySelector(targetId);
                if (target) {
                    event.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    document.querySelectorAll('[data-copy-target]').forEach(button => {
        button.addEventListener('click', async () => {
            const targetSelector = button.getAttribute('data-copy-target');
            const target = document.querySelector(targetSelector);
            if (!target) return;

            try {
                await navigator.clipboard.writeText(target.innerText.trim());
                const original = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check mr-1"></i>Copied';
                setTimeout(() => (button.innerHTML = original), 1600);
            } catch (err) {
                console.error('Copy failed', err);
                alert('Copy failed. Please copy manually.');
            }
        });
    });
});


