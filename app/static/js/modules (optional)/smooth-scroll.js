//SMOOTH SCROLL
$(".smooth-scroll").on('click', 'a', function(event) {
    event.preventDefault();
    var elAttr = $(this).attr('href');
    var offset = ($(this).attr('data-offset') ? $(this).attr('data-offset') : 0);
    $('body,html').animate({
        scrollTop: $(elAttr).offset().top - offset
    }, 700);
});