function replaceDivWithLoader() {
    var replace = document.getElementById("replace");
    var loader = document.getElementById("loader");

    // Hide the original div and show the loader
    replace.style.display = "none";
    loader.style.display = "flex";

}

window.onload = function() {
    var forms = document.getElementsByTagName("form");

    for (var i = 0; i < forms.length; i++) {
        forms[i].addEventListener('submit', function(event) {
    
            if (!this.checkValidity()) {
                // If the form is invalid, stop the form submission
                event.preventDefault();
                // Maybe notify the user that there are invalid inputs
            } else {
                // All the inputs are valid
                // Here you can call the function to replace the div with the loader
                replaceDivWithLoader();
                // Then let the form submit normally
            }
        });
    }
}