function replaceDivWithLoader() {
    var replace = document.getElementById("replace");
    var loader = document.getElementById("loader");

    // Hide the original div and show the loader
    replace.style.display = "none";
    loader.style.display = "flex";

}

window.onload = function() {
    var loadInputs = document.getElementsByClassName("load");

    for(var i = 0; i < loadInputs.length; i++) {
        loadInputs[i].addEventListener('click', replaceDivWithLoader);
    }
}