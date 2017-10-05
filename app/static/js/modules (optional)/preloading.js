//Preloading script

$(document).ready(function () {
    $('#preloader-markup').load("mdb-addons/preloader.html", function() {
        $('#preloader-markup').fadeOut('slow');
    });
});
