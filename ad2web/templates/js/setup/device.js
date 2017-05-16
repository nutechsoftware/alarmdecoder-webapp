<script type="text/javascript">

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
    $(document).ready(function() {

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
                    alert('DSC Partition and Slot has to be between 1 and 88');
                    event.preventDefault();
                }
            }
        });
    });
</script>
