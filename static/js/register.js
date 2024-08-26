function showStep(step) {
    // Hide all steps
    document.querySelectorAll('.step-form').forEach(el => el.style.display = 'none');
    // Show the current step
    document.getElementById('step' + step).style.display = 'block';
}

// Show the first step initially
showStep(1);
