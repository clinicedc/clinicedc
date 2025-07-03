document.addEventListener('DOMContentLoaded', function () {
    const delay = window.adminSaveDelay || 0; // fallback to 0 seconds
    const buttonNames = ['_save', '_continue', '_addanother',' _savenext'];

    buttonNames.forEach(name => {
        const button = document.querySelector(`input[name="${name}"]`);
        if (button) {
            button.addEventListener('click', function () {
                // Delay disabling to allow form submission
                setTimeout(() => {
                    button.disabled = true;

                    // Re-enable after 3 seconds in case submission fails
                    setTimeout(() => {
                        button.disabled = false;
                    }, delay);
                }, 100);
            });
        }
    });
});
