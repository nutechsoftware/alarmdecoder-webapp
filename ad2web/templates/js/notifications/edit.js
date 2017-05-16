<script type="text/javascript">
    var iCnt = 0;

    $(document).ready(function() {
        $(".form-box fieldset").prepend($('#notification-type-wrapper'));

        $('#delay_field').prepend("<label for='delay_field'>Delay Settings</label>");
        $('#delay_field').accordion({
            collapsible: true,
            active: false
        });
        // Accordion the Notify On.. settings.
        $('#subscriptions div.controls').accordion({
            collapsible: true,
            active: false
        });

        $('#time_field').prepend("<label for='time_field'>Time Restrictions</label>");
        $('#time_field').accordion({
            collapsible: true,
            active: false
        });

        $('#form_field').prepend("<label for='form_field'>{{ TYPES[notification.type]|capitalize }} Settings</label>");
        $('#form_field').accordion({
            collapsible: true,
            active: false
        });

        $('#subscriptions div.controls span.help-inline').remove();

        var inputs = document.getElementsByTagName('input');
        for( var inputCnt = 0; inputCnt < inputs.length; inputCnt++)
        {
            if( inputs[inputCnt].type == 'text' && inputs[inputCnt].name.indexOf("custom_key") != -1 )
                iCnt++;
        }

        $('#custom_values').css("list-style-type", "none");
        for( var cnt = 0; cnt < iCnt; cnt++ )
        {
            $("label[for='custom_values-" + cnt + "']").hide();
            $("label[for='custom_values-" + cnt + "-csrf_token']").hide();
        }
        createFormTooltip('#description', 'Name of notification for display in list of notifications.');

        if( '{{ TYPES[notification.type] }}' == 'email' )
        {
            createFormTooltip('#form_field-source', 'Emails will come from this address.');
            createFormTooltip('#form_field-destination', 'Emails will go to this address.');
            createFormTooltip('#form_field-server', 'Email server to use.\n\nGmail Example: smtp.gmail.com');
            createFormTooltip('#form_field-port', 'Port email server listens on.\nMany ISPs filter default ports, please verify what port your server utilizes.\n\nGmail Example: 587');
            createFormTooltip('#form_field-tls', 'Enable TLS security?  Yes for Gmail!');
            createFormTooltip('#form_field-authentication_required', 'Does your server require authentication for your user?\n\nGmail Example: Yes');
            createFormTooltip('#form_field-username', 'Username to authenticate with to the mail server.\n\nFor Gmail this is the part before @gmail.com');
            createFormTooltip('#form_field-password', 'The password for your email user.');
        }
        if( '{{ TYPES[notification.type] }}' == 'googletalk' )
        {
            createFormTooltip('#form_field-source', 'Address you would like messages to originate from.');
            createFormTooltip('#form_field-password', 'The password for the source address.');
            createFormTooltip('#form_field-destination', 'The address you would like to send messages to.');
        }
        if( '{{ TYPES[notification.type] }}' == 'pushover' )
        {
            createFormTooltip('#form_field-token', 'Your pushover application API Token');
            createFormTooltip('#form_field-user_key', 'Your user or group key');
            createFormTooltip('#form_field-priority', 'Message Priority');
            createFormTooltip('#form_field-title', 'Title of your Message');
        }
        if( '{{ TYPES[notification.type] }}' == 'twilio' )
        {
            createFormTooltip('#form_field-account_sid', 'The Twilio Account SID for this User.');
            createFormTooltip('#form_field-auth_token', 'Your Twilio User Auth Token.');
            createFormTooltip('#form_field-number_to', 'Number to send SMS to');
            createFormTooltip('#form_field-number_from', 'Number SMS comes from - Must be a valid Twilio phone number.');
        }
        if( '{{ TYPES[notification.type] }}' == 'NMA' )
        {
            createFormTooltip('#form_field-api_key', 'The NotifyMyAndroid API Key');
            createFormTooltip('#form_field-app_name', 'The Application Name to show in notifications.');
            createFormTooltip('#form_field-nma_priority', 'Message Priority');
        }
        if( '{{ TYPES[notification.type] }}' == 'prowl')
        {
            createFormTooltip('#form_field-prowl_api_key', 'Your Prowl API Key');
            createFormTooltip('#form_field-prowl_app_name', 'Application Name to show in notifications.');
            createFormTooltip('#form_field-prowl_priority', 'Prowl Message Priority');
        }
        if( '{{ TYPES[notification.type] }}' == 'growl' )
        {
            createFormTooltip('#form_field-growl_hostname', 'Growl server to send notification to');
            createFormTooltip('#form_field-growl_port', 'Growl server listen port');
            createFormTooltip('#form_field-growl_password', 'The password for the growl server');
            createFormTooltip('#form_field-growl_title', 'Notification Title');
            createFormTooltip('#form_field-growl_priority', 'Growl Message Priority');
        }
        if( '{{ TYPES[notification.type] }}' == 'custom' )
        {
            createFormTooltip('#form_field-custom_url', 'The URL to POST data to.');
            createFormTooltip('#form_field-custom_path', 'The Path on the server to POST to.');
            createFormTooltip('#form_field-is_ssl', 'HTTP or HTTPS?');
            createFormTooltip('#form_field-post_type', 'Does the URL expect urlencode, json, or xml data?');
            createFormTooltip('#form_field-add_field', 'Click me to add custom fields to notification.');
        }

        $(document.body).on('click', '.remove_field', function(e) {
            e.preventDefault();
            $(this).parent('div').remove();
            iCnt--;
        });
        $(document.body).on('touchend', '.remove_field', function(e) {
            e.preventDefault();
            $(this).parent('div').remove();
            iCnt--;
        });

    });

function addField()
{
    var newInput = '<div class="control-group" id="form_field-custom_values-' + iCnt + '"><div class="controls"><div class="control-group" style="display: inline-block;"><label for="form_field-custom_values-' + iCnt + '-custom_key" class="control-label">Custom Key</label><div class="controls"><input type="text" id="form_field-custom_values-' + iCnt + '-custom_key" name="form_field-custom_values-' + iCnt + '-custom_key"/>&nbsp;</div></div><div class="control-group" style="display: inline-block;"><label for="form_field-custom_values-' + iCnt + '-custom_value" class="control-label">Custom Value</label><div class="controls"><input type="text" id="form_field-custom_values-' + iCnt + '-custom_value" name="form_field-custom_values-' + iCnt + '-custom_value" class="custom_value"/></div><span class="help-inline"></span></div><a href="#" id="remove_field' + iCnt + '" class="remove_field"><img alt="Remove" title="Remove" src="{{ url_for("static", filename="img/red_x.png") }}"></a></div>';
    $('#form_field-add_field-group').before(newInput);
    iCnt++;
}
</script>
