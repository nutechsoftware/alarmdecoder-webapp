/* Author: Wilson Xu */

/* Add a flash message notification to the DOM */
function add_flash_message(message, category)
{
    var htmlStr = '<div class="alert alert-' + category + '" data-dismiss="alert"><button type="button" class="close" data-dismiss="alert">x</button>' + message + '</div>';
    $('#flash_message_container').append(htmlStr);
}

/* Determine if text is selected in any input */
function isTextSelected(input)
{
    if( typeof input.selectionStart == "number" )
    {
        return input.selectionStart == 0 && input.selectionEnd == input.value.length;
    }
    else if( typeof document.selection != "undefined")
    {
        input.focus();
        return document.selection.createRange().text == input.value;
    }
}

function hide_flask_message_container() {
    $('#flash_message_container').slideUp('fast');
}

$(document).ready(function() {
    decoder = new AlarmDecoder();
    decoder.init();

    $('.alert').on('click', function(e) {
        $(this).hide();
    });

    $('.alert').on('touchend', function(e) {
        $(this).hide();
    });
    if( !isiPad )
    {
        $('#wrap').css('overflow-x', 'hidden');
    }
})
