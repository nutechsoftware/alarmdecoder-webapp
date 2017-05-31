<script type="text/javascript">
$(document).ready(function() {
    var cert_text = null;
    var cert_key = null;
    $('#cert').on('click', function() {
        var original = $('#cert_input')[0];
        var clone = $(original).clone().attr('id', 'cert_input_clone');
        var saveHtml = $(original).html();
        $(original).html('');
        $(clone).dialog({
            title: "Certificate Cert: Hit Ctrl-C to Copy",
            width: 800,
            height: 550,
            modal: true,
            open: function(event, ui) {
                cert_text = $(saveHtml).text();
                $('<textarea id="tmp"/>').appendTo($(this)).val(cert_text).focus().select();
            },
            close: function(event, ui) {
                $('#tmp').remove();
                $(clone).remove();
                $(original).html(saveHtml);
            },
            buttons: [
            {
                text: 'Ok',
                click: function() {
                    $(this).dialog("close");
                },
                class: 'btn btn-primary',
            }],
        }).keyup(function(e) {
            if( e.keyCode == 67 && e.ctrlKey )
            {
                if( isTextSelected($('#tmp')[0]) )
                {
                    $(this).dialog("close");
                }
                else
                {
                    alert("Please select the text.");
                }
            }
        });
    });
    $('#key').on('click', function() {
        var original = $('#cert_key')[0];
        var clone = $(original).clone().attr('id', 'cert_key_clone');
        var saveHtml = $(original).html();
        $(original).html('');
        $(clone).dialog({
            title: "Certificate Key: Hit Ctrl-C to Copy",
            width: 800,
            height: 680,
            modal: true,
            open: function(event, ui) {
                cert_key = $(saveHtml).text();
                $('<textarea id="tmp"/>').appendTo($(this)).val(cert_key).focus().select();
            },
            close: function(event, ui) {
                $('#tmp').remove();
                $(clone).remove();
                $(original).html(saveHtml);
            },
            buttons: [
            {
                text: 'Ok',
                click: function() {
                    $(this).dialog("close");
                },
                class: 'btn btn-primary', 
            }],
        }).keyup(function(e) {
            if( e.keyCode == 67 && e.ctrlKey )
            {
                if( isTextSelected($('#tmp')[0]) )
                {
                    $(this).dialog("close");
                }
                else
                {
                    alert("Please select the text.");
                }
            }
        });
    });


    if( $('#revokeca').length )
    {
        $('#revokeca').confirm({
            title: 'Revoke CA?',
            text: 'This will invalidate all existing certificates.  Are you sure?',
        });
    }
});
</script>
