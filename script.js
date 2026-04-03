// script.js

function initializePasswordToggle() {
    // Find all password containers on the page
    const passwordContainers = document.querySelectorAll('.password-container');

    passwordContainers.forEach(container => {
        const passwordInput = container.querySelector('input[type="password"], input[type="text"]');
        const toggleIcon = container.querySelector('.toggle-password');

        if (passwordInput && toggleIcon) {
            toggleIcon.addEventListener('click', () => {
                // Toggle the type of the password input field
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                
                // Toggle the eye icon SVG
                if (type === 'password') {
                    // Show the 'eye' icon
                    toggleIcon.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                            <path d="M10 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z" />
                            <path fill-rule="evenodd" d="M.664 10.59a1.651 1.651 0 0 1 0-1.18l.82-1.425a1.651 1.651 0 0 1 1.516-.865h12.878a1.651 1.651 0 0 1 1.516.865l.82 1.425a1.651 1.651 0 0 1 0 1.18l-.82 1.425a1.651 1.651 0 0 1-1.516.865H3.001a1.651 1.651 0 0 1-1.516-.865l-.82-1.425ZM5.525 12a4.475 4.475 0 0 0 8.95 0H5.525Z" clip-rule="evenodd" />
                        </svg>`;
                } else {
                    // Show the 'eye-slash' icon
                    toggleIcon.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                            <path fill-rule="evenodd" d="M3.28 2.22a.75.75 0 0 0-1.06 1.06l14.5 14.5a.75.75 0 1 0 1.06-1.06l-1.745-1.745a10.029 10.029 0 0 0 3.3-4.243c-1.28-2.2-4.43-3.977-7.62-3.977a6.231 6.231 0 0 0-2.036.32l-1.04-.972A7.728 7.728 0 0 0 10 5c-3.19 0-6.335 1.777-7.62 3.977a10.03 10.03 0 0 0-1.14 2.22l-1.832-1.832ZM10 12.5a2.5 2.5 0 0 1-2.5-2.5 2.5 2.5 0 0 1 .11-1.79l-1.009-1.01a4.5 4.5 0 1 0 5.197-5.197l-1.01 1.01A2.5 2.5 0 0 1 10 12.5Z" clip-rule="evenodd" />
                        </svg>`;
                }
            });
        }
    });
}

// Run the function when the page loads
document.addEventListener('DOMContentLoaded', initializePasswordToggle);