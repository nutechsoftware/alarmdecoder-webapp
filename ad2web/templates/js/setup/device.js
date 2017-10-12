{% include 'js/setup/enrollment.js' %}
<script type="text/javascript">
    addresses = [];
    new_address = 18;
    aui_retries = 0;

    //detect if mobile
    function isMobile()
    {
        if( $('html').hasClass('mobile') == true && $('html').hasClass('tablet') == false )
            return true;
        return false;
    }
    //detect if tablet
    function isTablet()
    {
        if( $('html').hasClass('tablet') == true )
            return true;

        return false;
    }
    //is local storage supported?
    function storageSupported()
    {
        if( Modernizr.localstorage)
            return true;
        return false;
    }

    function buttonAtRight(button, element, offset)
    {
        $(button).position({
            my: "right",
            at: "right+" + offset,
            of: $(element)
        });
    }

    function bindValueToInput(value, input)
    {
        $(input).val(value);
    }

    function calculateMask()
    {
        var mask = 0x00000000;

        // Ademco
        if ($('#panel_mode-0:checked').val())
        {

            for (var i = 0; i < 32; i += 8)
            {
                var temp_mask = 0x00;

                for (var j = 0; j < 8; j++)
                    temp_mask |= $("#address_checkbox_" + (i + j + 1)).is(":checked") ? (1 << j) : 0;

                mask |= temp_mask;
                if (i < 24)
                    mask <<= 8;
            }
        }
        // DSC
        else if ($('#panel_mode-1:checked').val())
        {
            for( i = 1; i < 33; i++ )
            {
                if($("#address_checkbox_" + i).is(':checked'))
                    mask |= 1;
                else
                    mask |= 0;
                              
                if( i < 32 ) 
                    mask <<= 1;
            }
        }

        return ("00000000" + (mask >>> 0).toString(16)).slice(-8).toUpperCase();
    }

    function refreshMaskDialog(mask_element)
    {
        var current_mask = parseInt($(mask_element).val(), 16);
        var label_prefix_text = "Address";
        var is_dsc = false;

        var table = $("#keypad-mask-table");
        $(table).empty();

        // Switch things around if DSC is selected
        if ($('#panel_mode-1:checked').val()) {
            is_dsc = true;
            label_prefix_text = "Partition";
            $('#keypad-mask-instructions').text('Please select the partitions you would like to see messages for:');
        }

        // Determine checkbox state based on mask.
        for (var shifted = current_mask, checked = [], i = 31; shifted; shifted >>>= 1, i--)
        {
            var value = shifted & 1;

            if (!is_dsc)
            {
                var subset = Math.floor(i / 8);
                var subset_index = 7 - (i - subset * 8);
                checked[(subset * 8) + subset_index] = Boolean(value);
            }
            else
                checked[i] = Boolean(value);
        }

        // Build up the table
        var row = $('<tr/>');
        for (var i = 0; i < 32; i++) {
            var data = $("#template-table td").clone();
            var label = $(data).find("label");
            var input = $(data).find("input");

            $(label)
                .prop("for", "address_checkbox_" + (i + 1))
                .text(("00" + (i + (is_dsc ? 1 : 0))).slice(-2));

            $(input)
                .prop("id", "address_checkbox_" + (i + 1))
                .prop("name", "address_checkbox_" + (i + 1))
                .prop("checked", checked[i] === true);

            if (i % 8 == 0 && i != 0)
            {
                $(row).appendTo(table);
                row = $('<tr/>');
            }

            $(data).appendTo(row);
        };

        $(row).appendTo(table);
    }
    $(document).ready(function() 
    {
        $.fn.spin.presets.flower = {
            lines: 13,
            length: 30,
            width: 10,
            radius: 30,
            className: 'spinner',
        }

        mobile = isMobile();
        tablet = isTablet();

        $(function() {
            FastClick.attach(document.body);
        });

        createFormTooltip('[id^=panel_mode]', 'Which type of panel do you have?');
        createFormTooltip('#keypad_address', 'The address of your keypad.  18 default.\n\nFor SE Panels, Address 31 must be set.\n\nDSC Partition between 1 and 8.');
        createFormTooltip('#address_mask', 'This features allows you to select specific keypad addresses to listen to. 32-bit Hex Number. \n\nDefault: FFFFFFFF');
        createFormTooltip('#internal_address_mask', 'The internal address mask allows you to further filter messages to be interpreted by the webapp. 32-bit Hex Number. \n\nDefault: FFFFFFFF');
        createFormTooltip('[id^=zone_expanders]', 'Enable zone expander emulation support?');
        createFormTooltip('[id^=relay_expanders]', 'Enable relay expander emulation support?');
        createFormTooltip('#lrr_enabled', 'Enable Long Range Radio emulation support?');
        createFormTooltip('#deduplicate', 'The availability to remove repetitive messages. This in conjunction with the Address Mask will remove duplicate alarm messages the panel produces.');
        buttonAtRight("#address_mask_builder", "#address_mask", 150);
        buttonAtRight("#internal_address_mask_builder", "#internal_address_mask", 150);

        $("#exit").on('mousedown', function() {
            $('#dialog').dialog("close");
        });
        $("#exit").on('touchstart', function() {
            $('#dialog').dialog("close");
        });

        if( !tablet && !mobile )
        {
            $("#address_mask_builder").click(function() {
                refreshMaskDialog('#address_mask');

                $('#dialog').dialog({
                    modal: true,
                    minWidth: 1000,
                    maxWidth: 1000,
                    close: function() {
                        var mask = calculateMask();
                        bindValueToInput( mask, "#address_mask");
                    }
                });
            });
        }
        else
        {
            if( mobile )
            {
                $("#address_mask_builder").on('touchstart', function() {
                    refreshMaskDialog('#address_mask');

                    $('#dialog').dialog({
                        modal: true,
                        minWidth: 400,
                        position: { my: "center", at: "center", of: window },
                        close: function() {
                            var mask = calculateMask();
                            bindValueToInput( mask, "#address_mask");
                        }
                    });
                });
            }
            if( tablet )
            {
                $("#address_mask_builder").on('touchstart', function() {
                    refreshMaskDialog('#address_mask');

                    $('#dialog').dialog({
                        modal: true,
                        minWidth: 725,
                        position: { my: "center", at: "center", of: window },
                        close: function() {
                            var mask = calculateMask();
                            bindValueToInput( mask, "#address_mask");
                        }
                    });
                });
            }
        }

        if( !tablet && !mobile )
        {
            $("#internal_address_mask_builder").click(function() {
                refreshMaskDialog('#internal_address_mask');
                $('#dialog').dialog({
                    modal: true,
                    minWidth: 1000,
                    maxWidth: 1000,
                    close: function() {
                        var mask = calculateMask();
                        bindValueToInput( mask, "#internal_address_mask");
                    }
                });
            });
        }
        else
        {
            if( mobile )
            {
                $("#internal_address_mask_builder").on('touchstart', function() {
                    refreshMaskDialog('#internal_address_mask');

                    $('#dialog').dialog({
                        modal: true,
                        minWidth: 400,
                        position: { my: "center", at: "center", of: window },
                        close: function() {
                            var mask = calculateMask();
                            bindValueToInput( mask, "#internal_address_mask");
                        }
                    });
                });
            }
            if( tablet )
            {
                $("#internal_address_mask_builder").on('touchstart', function() {
                    refreshMaskDialog('#internal_address_mask');

                    $('#dialog').dialog({
                        modal: true,
                        minWidth: 725,
                        position: { my: "center", at: "center", of: window },
                        close: function() {
                            var mask = calculateMask();
                            bindValueToInput( mask, "#internal_address_mask");
                        }
                    });
                });
            }
        }
        $('#getDeviceInfo').button("disable");
        PubSub.subscribe('message', function(type, msg) 
        {
            if( state == states['getCode'] && msg.message_type != "aui" )
            {
                aui_retries++;
                if( aui_retries > 2 )
                {
        		    state = states['unsupported'];
                    $('#info_dialog').dialog("close");
                    $('#loading').stop();
                    $('#loading').hide();
                    $.alert('Seems we are not supporting AUI commands at this time.  Does your panel support AUI?  Is AUI enabled?  If not, proceed with manual setup.');
                }
            }
            if( msg.message_type == "panel" )
            {
                if( state == states['programmingMode'] )
                {
                    if( msg.programming_mode && programmingModeRetries <= 4)
                    {
                        inProgrammingMode = true;
                        state = states['programmingModeDone'];
                    }
                    else
                    {
                        if( programmingModeRetries > 4 )
                        {
                            state = states['programmingModeDone'];
                        }
                        programmingModeRetries++;
                        wait2seconds();
                        wait2seconds();
                    }
                }
            }
            if( state == states['programmingModeDone'] )
            {
                wait2seconds();
                if( unlockSlot != 0 )
                {
                    tryUnlock(unlockSlot);
                    $('#loading').stop();
                    $('#loading').hide();
                }
                else
                {
                    $.alert('No keypad slots found.');
                    state = states['doneDone'];
                    $('#loading').stop();
                    $('#loading').hide();
                }
            }

            if( state == states['unlockDone'] )
            {
                $.alert('Done attempting to enroll, please verify settings and click next to continue');
                state = states['doneDone'];
            }
            if( msg.message_type == "aui" )
            {
        		aui_retries = 0;
                prefix = getAUIPrefix(msg.value);
                value = msg.value.trim();

                if( state == states['getDeviceCount'] )
                {
                    ascii = parseAUIMessage(prefix, value);
                    $('#numdevices').css('font-weight', 'Bold');
                    $('#numdevices').text('Number of Devices: ' + ascii );
                    $('#numdevices').show();
                    decoder.emit('keypress', 'K18\r\n');
                    if( isNaN(ascii) )
                    {
                        getDeviceCount();
                    }
                    else
                    {
                        numberOfDevices = ascii;
                        state = states['getDeviceCountDone'];
                        getDeviceDetails();
                    }
                }
                if( state == states['getCode'] && prefix == '0d' ) //(81)
                {
                    $('#loading').stop();
                    $('#loading').hide();
                    $('#getDeviceInfo').button("disable");
                    ascii = parseAUIMessage(prefix, value);
                    $('#asciicode').css("font-weight", "Bold");
                    $('#asciicode').text('Potential Installer Code: ' + ascii);
                    $('#asciicode').show();
                    iCode = ascii;
                    state = states['getCodeDone'];
                    decoder.emit('keypress', "K18\r\n");
                    getPanelType();
                }
                if( state == states['getPanelType'] )
                {
                    if( isNaN(iCode) )
                    {
                        state = states['getCode'];
                        if( retries < 3 )
                        {
                            getCode();
                        }
                        else
                        {
                            state = states['unsupported'];
                            $.alert("Unable to get response from AUI command.  Possibly unsupported. Setting Address 31 in case of SE Panel");
                            new_address = 31;
                            $('#keypad_address').val(new_address);
                        }
                        retries++;
                    }
                    else
                    {
                        ascii = parseAUIMessage(prefix, value);
                        $('#panel_version').css('font-weight', 'Bold');
                        $('#panel_version').text('Panel Model: ' + ascii);
                        $('#panel_version').show();
                        state = states['getPanelTypeDone'];
                        decoder.emit('keypress', "K18\r\n");
                        panelType = ascii;
                        getPanelFirmware(); 
                    }
                }
                if( state == states['getFirmware'])
                {
                    ascii = parseAUIMessage(prefix, value);
                    $('#panel_firmware').css('font-weight', 'Bold');
                    $('#panel_firmware').text('Panel Firmware Version: ' + ascii);
                    $('#panel_firmware').show();
                    state = states['getFirmwareDone'];
                    decoder.emit('keypress', "K18\r\n");
                    $('#getDeviceInfo').button("enable");
                }
                if( state == states['getDeviceDetails'] )
                {
                    if( isNaN(numberOfDevices) )
                    {
                        getDeviceCount();
                    }
                    else
                    {
                        details = parseAUIMessage(prefix, value);

                        addr = parseInt(details['address']);
                        if( !in_array(addresses, addr ) )
                        {
                            if( details['type'] == 'Keypad' )
                            {
                                $('#devices').css('font-weight', 'Bold');
                                $('#devices').show();
                                $('#devices').append("<br/>Address: " + details['address'] + " Type: " + details['type']);
                                addresses.push(addr);
                            }
                        }
                        if( count > parseInt(originalNumDevices) )
                        {
                            state = states['getDeviceDetailsDone'];
                            max_address = Math.max.apply(null, addresses);
                            if( panelDefinitions[panelType] === "undefined" )
                            {
                                $.alert("Unable to find your panel definition of addresses in the javascript, please try manually entering your information");
                            }
                            else
                            {
                                if( panelDefinitions[panelType][max_address +1] !== "undefined" )
                                {
                                    if( addresses.length == 0 )
                                        new_address = 17;
                                    else
                                        new_address = max_address + 1;

                                    $('#keypad_address').val(new_address);
                                    unlockSlot = panelDefinitions[panelType][new_address];
                                    $('.progress_label').hide();
                                    $('#progressbar').hide();
                                    $.confirm({
                                        content: "Try to unlock and set address " + new_address + "?  Please make sure AUI keypads (TuxedoTouch etc) are unplugged to avoid command collisions.",
                                        title: "Enroll Attempt",
                                        confirm: function(button) {
                                            $('#info_dialog').dialog("close");
                                            $('#loading').show();
                                            $('#loading').spin('flower');
                                            programmingMode();
                                        },
                                        cancel: function(button) {
                                        },
                                        confirmButton: "Yes",
                                        cancelButton: "No",
                                        post: false,
                                    });
                                }
                                else
                                {
                                    if( panelDefinitions[panelType][0] == "31" )
                                    {
                                        $.alert("Somehow we've made it this far with an SE Panel?? Setting to address 31.");
                                        $('#keypad_address').val(31);
                                    }
                                    else
                                    {
                                        $.alert("Unable to find address slot in panel definition, please confirm you have a free keypad slot and your panel addresses are defined within the app. (enrollment.js)");
                                    }
                                }
                            }
                            $('#getDeviceInfo').button("disable");
                            $('#getPanelInfo').prop("disabled", false);
                        }
                        decoder.emit('keypress', "K18\r\n");
                    }
                }
            }
        });

        PubSub.subscribe('test', function(type, msg) {
            result_text = {
                'PASS': '<span style="color:green">&#10004;</span>',
                'FAIL': '<span style="color:red">&#10008;</span>',
                'TIMEOUT': '<span style="color:orange">&#9888;</span>'
            };

            result = result_text[msg.results] + ' : ' + msg.details;
        });

        $('#getPanelInfo').on('click', function() {
$.confirm({
                content: "WARNING: This can have adverse effects on some panels, specifically DSC panels.  Do you wish to continue?",
                title: "Get Panel Info Confirmation",
                confirm: function(button) {
                    $('#loading').show();
                    $('#loading').spin('flower');
                    $('#info_dialog').dialog({
                        title: "Panel Information",
                        modal: false,
                        minWidth: 450,
                        maxWidth: 450,
                        height: 450,
                        position: ['center', 80],
                        buttons: {
                            "getDeviceInfo": {
                                text: "Get Device Info",
                                id: "getDeviceInfo",
                                click: function() {
                                    $('.progress_label').show();
                                    $('#progressbar').show();
                                    $('#progressbar').progressbar({
                                        change: function() {
                                            $('.progress_label').text("Current Progress: " + $('#progressbar').progressbar("value") + "%" );
                                        }
                                    });
                                    $('#progressbar').progressbar('option', 'value', 0);
                                    getDeviceCount();
                                }
                            }
                        },
                        close: function() {
                            $('#info_dialog').hide();
                            $('#panel_version').empty();
                            $('#panel_firmware').empty();
                            $('#asciicode').empty();
                            $('#numdevices').empty();
                            $('#devices').empty();
                            addresses = [];
                            $('#getPanelInfo').prop("disabled", false);
                            $('#loading').stop();
                            $('#loading').hide();
                        }
                    });
                    $('#getDeviceInfo').button("disable");
                    $('#info_dialog').show();
                    retries = 0;
                    $('#getPanelInfo').prop("disabled", true);
                    setConfigBits();
                    getCode();
                },
                cancel: function(button) {
                },
                confirmButton: "Yes",
                cancelButton: "No",
                post: false,
            });
        });
        var form = document.getElementsByTagName("form");
        $(form).change(function() {
            selected_value = $("input[name='panel_mode']:checked").val();

            if( selected_value == 1 )
            {
                $('#getPanelInfo').hide();
                $('#honeywellHelper').hide();
            }
            else
            {
                $('#getPanelInfo').show();
                $('#honeywellHelper').show();
            }
        });
    });

    $('body').ready(function() {
        var mode = $('#panel_mode-1:checked').val();
        var label = $("label[for='keypad_address']");
        if( mode == 1 )
            label.html('Partition and Slot');
        else
            label.html('Keypad Address');

        function set_form_visible(val) {
            $('[id^=zone_expanders]').closest('.control-group').toggle(val);
            $('[id^=relay_expanders]').closest('.control-group').toggle(val);
            $('#lrr_enabled').closest('.control-group').toggle(val);
            $('#deduplicate').closest('.control-group').toggle(val);

            buttonAtRight("#address_mask_builder", "#address_mask", 150);
            buttonAtRight("#internal_address_mask_builder", "#internal_address_mask", 150);
        }

        if ($('#panel_mode-1:checked').val()) {
            set_form_visible(false);
        }

        $('[id^=panel_mode]').change(function(event) {
            switch($(event.target).val()) {
                case '0':
                    set_form_visible(true);
                    $('#keypad_address').val(18);
                    label.html('Keypad Address');
                    break;

                case '1':
                    label.html('Partition and Slot');
                    keypad_address_val = $('#keypad_address').val();
                    if( keypad_address_val < 1 || keypad_address_val > 88 )
                        $('#keypad_address').val(11);

                    set_form_visible(false);
                    break;
            }
        });
        $('#buttons-next').on('click', function(event) {
            keypad_address_val = $('#keypad_address').val();

            mode = $('#panel_mode-1:checked').val();
            if( mode == 1 )
            {
                if(keypad_address_val < 1 || keypad_address_val > 88 )
                {
                    $.alert('DSC Partition and Slot has to be between 1 and 88');
                    event.preventDefault();
                }
            }
        });
    });
</script>
