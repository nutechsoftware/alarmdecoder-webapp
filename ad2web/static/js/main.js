/* Author: Wilson Xu */

function add_flash_message(message, category)
{
    var htmlStr = '<div class="alert alert-' + category + '"><button type="button" class="close" data-dismiss="alert">x</button>' + message + '</div>';
    $('#flash_message_container').append(htmlStr);
}

function hide_flask_message_container() {
    $('#flash_message_container').slideUp('fast');
}

$(document).ready(function() {
    /* Show and hide flash message. */
    //$('#flash_message_container').slideDown(function() {
        //setTimeout(hide_flask_message_container, 3000);
    //});
    //
    decoder = new AlarmDecoder();
    decoder.init();
})
