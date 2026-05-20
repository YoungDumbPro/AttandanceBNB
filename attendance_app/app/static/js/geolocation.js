/**
 * Geolocation handling for attendance check-in.
 * Captures GPS coordinates using the browser's Geolocation API.
 */

/**
 * Get user's current GPS location and populate hidden form fields.
 * Called before check-in form submission.
 * 
 * @param {string} formId - The ID of the form to submit after getting location.
 */
function getLocation(event, formId) {
    event.preventDefault();

    const form = document.getElementById(formId);
    const latField = document.getElementById('latitude');
    const lngField = document.getElementById('longitude');
    const submitBtn = document.getElementById('checkin-btn');

    if (!form) {
        console.warn('Check-in form not found.');
        return;
    }

    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span><br><span>Getting location...</span>';
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Success - populate coordinates
                latField.value = position.coords.latitude;
                lngField.value = position.coords.longitude;
                
                // Submit the form
                form.submit();
            },
            function(error) {
                // Error or denied - submit without coordinates
                console.warn('Geolocation error:', error.message);
                
                // Clear fields (submit without GPS data)
                latField.value = '';
                lngField.value = '';
                
                // Submit anyway - GPS is optional
                form.submit();
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    } else {
        // Geolocation not supported - submit without coordinates
        console.warn('Geolocation is not supported by this browser.');
        form.submit();
    }
}

/**
 * Update the displayed current time every second.
 */
function updateClock() {
    const clockElement = document.getElementById('current-time');
    if (clockElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
        clockElement.textContent = timeString;
    }
}

// Start clock update interval
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
});
