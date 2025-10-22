// Collapsible component behavior
// Makes collapsible sections interactive

document.querySelectorAll('[data-component="collapsible"]').forEach(el => {
    const trigger = el.querySelector('[data-role="trigger"]');

    if (!trigger) return;

    trigger.addEventListener('click', () => {
        const isOpen = el.dataset.state === 'open';
        el.dataset.state = isOpen ? 'closed' : 'open';
    });

    // Keyboard accessibility
    trigger.setAttribute('tabindex', '0');
    trigger.setAttribute('role', 'button');
    trigger.setAttribute('aria-expanded', el.dataset.state === 'open');

    trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            trigger.click();
        }
    });
});
