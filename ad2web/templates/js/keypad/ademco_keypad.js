    <script type="text/javascript">
        String.prototype.replaceAt = function(index, str) {
            return this.substr(0, index) + str + this.substr(index + 1);
        }

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
        //visual beep or veep an element
        function veep(elem, times, speed)
        {
            if( times > 0 || times < 0 )
            {
                if( $(elem).hasClass("blink") )
                    $(elem).removeClass("blink");
                else
                    $(elem).addClass("blink");
            }

            clearTimeout(function() {
                veep( elem, times, speed );
            });

            if( times > 0 || times < 0 )
            {
                setTimeout(function() {
                    veep( elem, times, speed );
                }, speed);

                times -= .5;
            }
        }

        //preload our images into cache
        function preloadImages(array)
        {
            if( !preloadImages.list)
            {
                preloadImages.list = [];
            }
            for( var i = 0; i < array.length; i++ )
            {
                var img = new Image();
                img.src = array[i];
                preloadImages.list.push(img);
            }
        }
        function bindMouseDown(id, key, mobile_image, desktop_image )
        {
            $(id).on('mousedown', function() {
                $(this).attr("src", desktop_image );
                if( !tablet && !mobile )
                    decoder.emit('keypress', String(key));
            });
        }

//had to break this out from mousedown so it doesn't fire twice on touch devices
        function bindTouchStart(id, key, mobile_image, desktop_image )
        {
            $(id).on('touchstart', function() {
                $(this).attr("src", desktop_image );
                decoder.emit('keypress', String(key));
            });
        }

        function bindMouseUpTouchEnd(id, mobile_image, desktop_image )
        {
            $(id).on('mouseup touchend', function() {
                $(this).attr("src", desktop_image );
            });
        }

        function bindButtonEvents(id, key, mobile_image_down, desktop_image_down, mobile_image_up, desktop_image_up )
        {
            bindMouseDown(id, key, mobile_image_down, desktop_image_down );
            bindTouchStart(id, key, mobile_image_down, desktop_image_down );
            bindMouseUpTouchEnd(id, mobile_image_up, desktop_image_up );
        }

        //arrays of images to preload
        var ledImages = [
            "{{ url_for('static', filename='img/led-on-red.png') }}",
            "{{ url_for('static', filename='img/led-off.png') }}",
            "{{ url_for('static', filename='img/led-on.png') }}"
        ];
        var buttonImageListLarge = [
            "{{ url_for('static', filename='img/0-large-on.png') }}",
            "{{ url_for('static', filename='img/0-large.png') }}",
            "{{ url_for('static', filename='img/1-large-on.png') }}",
            "{{ url_for('static', filename='img/1-large.png') }}",
            "{{ url_for('static', filename='img/2-large-on.png') }}",
            "{{ url_for('static', filename='img/2-large.png') }}",
            "{{ url_for('static', filename='img/3-large-on.png') }}",
            "{{ url_for('static', filename='img/3-large.png') }}",
            "{{ url_for('static', filename='img/4-large-on.png') }}",
            "{{ url_for('static', filename='img/4-large.png') }}",
            "{{ url_for('static', filename='img/5-large-on.png') }}",
            "{{ url_for('static', filename='img/5-large.png') }}",
            "{{ url_for('static', filename='img/6-large-on.png') }}",
            "{{ url_for('static', filename='img/6-large.png') }}",
            "{{ url_for('static', filename='img/7-large-on.png') }}",
            "{{ url_for('static', filename='img/7-large.png') }}",
            "{{ url_for('static', filename='img/8-large-on.png') }}",
            "{{ url_for('static', filename='img/8-large.png') }}",
            "{{ url_for('static', filename='img/9-large-on.png') }}",
            "{{ url_for('static', filename='img/9-large.png') }}",
            "{{ url_for('static', filename='img/star-large-on.png') }}",
            "{{ url_for('static', filename='img/star-large.png') }}",
            "{{ url_for('static', filename='img/pound-large-on.png') }}",
            "{{ url_for('static', filename='img/pound-large.png') }}",
            "{{ url_for('static', filename='img/f1-fire-on.png') }}",
            "{{ url_for('static', filename='img/f1-fire.png') }}",
            "{{ url_for('static', filename='img/f2-police-on.png') }}",
            "{{ url_for('static', filename='img/f2-police.png') }}",
            "{{ url_for('static', filename='img/f3-medical-on.png') }}",
            "{{ url_for('static', filename='img/f3-medical.png') }}",
            "{{ url_for('static', filename='img/f4-led-text-on.png') }}",
            "{{ url_for('static', filename='img/f4-led-text.png') }}"
        ];

        var buttonImageListSmall = [
            "{{ url_for('static', filename='img/0-small-on.png') }}",
            "{{ url_for('static', filename='img/0-small.png') }}",
            "{{ url_for('static', filename='img/1-small-on.png') }}",
            "{{ url_for('static', filename='img/1-small.png') }}",
            "{{ url_for('static', filename='img/2-small-on.png') }}",
            "{{ url_for('static', filename='img/2-small.png') }}",
            "{{ url_for('static', filename='img/3-small-on.png') }}",
            "{{ url_for('static', filename='img/3-small.png') }}",
            "{{ url_for('static', filename='img/4-small-on.png') }}",
            "{{ url_for('static', filename='img/4-small.png') }}",
            "{{ url_for('static', filename='img/5-small-on.png') }}",
            "{{ url_for('static', filename='img/5-small.png') }}",
            "{{ url_for('static', filename='img/6-small-on.png') }}",
            "{{ url_for('static', filename='img/6-small.png') }}",
            "{{ url_for('static', filename='img/7-small-on.png') }}",
            "{{ url_for('static', filename='img/7-small.png') }}",
            "{{ url_for('static', filename='img/8-small-on.png') }}",
            "{{ url_for('static', filename='img/8-small.png') }}",
            "{{ url_for('static', filename='img/9-small-on.png') }}",
            "{{ url_for('static', filename='img/9-small.png') }}",
            "{{ url_for('static', filename='img/star-small-on.png') }}",
            "{{ url_for('static', filename='img/star-small.png') }}",
            "{{ url_for('static', filename='img/pound-small-on.png') }}",
            "{{ url_for('static', filename='img/pound-small.png') }}",
            "{{ url_for('static', filename='img/f1-fire-small-on.png') }}",
            "{{ url_for('static', filename='img/f1-fire-small.png') }}",
            "{{ url_for('static', filename='img/f2-police-small-on.png') }}",
            "{{ url_for('static', filename='img/f2-police-small.png') }}",
            "{{ url_for('static', filename='img/f3-medical-small-on.png') }}",
            "{{ url_for('static', filename='img/f3-medical-small.png') }}",
            "{{ url_for('static', filename='img/f4-led-text-small-on.png') }}",
            "{{ url_for('static', filename='img/f4-led-text-small.png') }}"
        ];

        var specialImageList = [
            "{{ url_for('static', filename='img/s1-off.png') }}",
            "{{ url_for('static', filename='img/s1-on.png') }}",
            "{{ url_for('static', filename='img/s2-off.png') }}",
            "{{ url_for('static', filename='img/s2-on.png') }}",
            "{{ url_for('static', filename='img/s3-off.png') }}",
            "{{ url_for('static', filename='img/s3-on.png') }}",
            "{{ url_for('static', filename='img/s4-off.png') }}",
            "{{ url_for('static', filename='img/s4-on.png') }}",
        ];
        //setup audio beeping
        var beep1 = new Audio("{{ url_for('static', filename='sounds/1beep.wav') }}");
        var beep2 = new Audio("{{ url_for('static', filename='sounds/2beep.wav') }}");
        var beep3 = new Audio("{{ url_for('static', filename='sounds/3beep.wav') }}");
        var beep4 = new Audio("{{ url_for('static', filename='sounds/4beep.wav') }}");
        var beep5 = new Audio("{{ url_for('static', filename='sounds/5beep.wav') }}");
        var beep6 = new Audio("{{ url_for('static', filename='sounds/6beep.wav') }}");
        var beep7 = new Audio("{{ url_for('static', filename='sounds/7beep.wav') }}");
        var mute = 0;
        var mobile = false;
        var tablet = false;

        if( isMobile() )
        {
            var keypadline1 = document.getElementById("keypad-line1");
            keypadline1.style.fontSize = "25px";
            var keypadline2 = document.getElementById("keypad-line2");
            keypadline2.style.fontSize = "25px";
        
        }

        const keypadSpecials = {
            FIRE: 0,
            POLICE: 1,
            MEDICAL: 2,
            SPECIAL_4: 3,
            SPECIAL_CUSTOM: 5,
            STAY: 6,
            AWAY: 7,
            CHIME: 8,
            RESET: 9,
            EXIT: 10
        };

        function checkConfirm(special_button_id, special_button_value)
        {
            if( special_button_id == keypadSpecials.SPECIAL_CUSTOM )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Custom Special Button",
                    confirm: function(button) {
                        add_flash_message("Custom Command Sent", "error");
                        decoder.emit('keypress', special_button_value);
                    },
                    cancel: function(button) {
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.FIRE )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Call the Fire Department",
                    confirm: function(button) {
                       add_flash_message("Fire Department notified.", "error");
                       decoder.emit('keypress', 1);
                    },
                    cancel: function(button) {
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.POLICE )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Call the Police Department",
                    confirm: function(button) {
                        add_flash_message("Police Department notified.", "error");
                        decoder.emit('keypress', 2);
                    },
                    cancel: function(button) {
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.MEDICAL )
            {
                 $.confirm({
                    content: "Are you sure?",
                    title: "Call the Medics",
                    confirm: function(button) {
                        add_flash_message("Medical Help notified.", "error");
                        decoder.emit('keypress', 3);
                    },
                    cancel: function(button) {
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.SPECIAL_4 )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Confirmation required",
                    confirm: function(button) {
                        add_flash_message("Notification sent.", "error");
                        decoder.emit('keypress', 4);
                    },
                    cancel: function(button) {
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });

            }
        }

        $(document).ready(function() {
            //detect mobile and tablet
            mobile = isMobile();
            tablet = isTablet();

            $('#check-mute').bootstrapToggle();
            $(function() {
                FastClick.attach(document.body);
            });
            //preload led images
            preloadImages(ledImages);

            //button Images
            preloadImages(buttonImageListLarge);
            preloadImages(specialImageList);

            special_image_defaults = { 0: buttonImageListSmall[25], 1: buttonImageListSmall[27], 2: buttonImageListSmall[29], 3: specialImageList[6], 5: specialImageList[0] };

            special_image_defaults_on = { 0: buttonImageListSmall[24], 1: buttonImageListSmall[26], 2: buttonImageListSmall[28], 3: specialImageList[7], 5: specialImageList[1] };

            //set image sources for buttons after preloaded
            $('#button-0').attr("src", buttonImageListLarge[1]);
            $('#button-1').attr("src", buttonImageListLarge[3]);
            $('#button-2').attr("src", buttonImageListLarge[5]);
            $('#button-3').attr("src", buttonImageListLarge[7]);
            $('#button-4').attr("src", buttonImageListLarge[9]);
            $('#button-5').attr("src", buttonImageListLarge[11]);
            $('#button-6').attr("src", buttonImageListLarge[13]);
            $('#button-7').attr("src", buttonImageListLarge[15]);
            $('#button-8').attr("src", buttonImageListLarge[17]);
            $('#button-9').attr("src", buttonImageListLarge[19]);
            $('#button-star').attr("src", buttonImageListLarge[21]);
            $('#button-pound').attr("src", buttonImageListLarge[23]);
            $('#button-F1').attr("src", special_image_defaults[{{special_buttons['special_1']}}]);
            $('#button-F2').attr("src", special_image_defaults[{{special_buttons['special_2']}}]);
            $('#button-F3').attr("src", special_image_defaults[{{special_buttons['special_3']}}]);
            $('#button-F4').attr("src", special_image_defaults[{{special_buttons['special_4']}}]);
            //check to see if we're going to play sounds or not if we've set the checkbox
            if( storageSupported() )
            {
                if( (checkmute = localStorage.getItem("mute")) !== null )
                    mute = parseInt(checkmute);

                if( mute == 1 )
                    $('#check-mute').bootstrapToggle('off');
                else
                    $('#check-mute').bootstrapToggle('on');
            }
            //handle messages from the AlarmDecoder
            PubSub.subscribe('message', function(type, msg) {
                cursor_location = -1;
                if( msg.message_type == 'panel')
                {
                    if( msg.cursor_location )
                        cursor_location = msg.cursor_location;

                    var lines = ['', '']
                    var armed = msg.armed_away | msg.armed_home;
                    var ready = msg.ready;
                    var beeps = 0;
                    var chime = msg.chime_on;

                    if( msg.beeps )
                    {
                        beeps = msg.beeps;
                    }

                    if( beeps > 0 )
                    {
                        veep('#keypad-line1', beeps, 100);
                        veep('#keypad-line2', beeps, 100);
                    }
                    if( mute == 0 )
                    {
                        try
                        {
                            switch(beeps)
                            {
                                case 1:
                                    beep1.load();
                                    beep1.play();
                                    break;
                                case 2:
                                    beep2.load();
                                    beep2.play();
                                    break;
                                case 3:
                                    beep3.load();
                                    beep3.play();
                                    break;
                                case 4:
                                    beep4.load();
                                    beep4.play();
                                    break;
                                case 5:
                                    beep5.load();
                                    beep5.play();
                                    break;
                                case 6:
                                    beep6.load();
                                    beep6.play();
                                    break;
                                case 7:
                                    beep7.load();
                                    beep7.play();
                                    break;
                                default:
                                    break;
                            }
                        }
                        catch(e)
                        {
                            if( window.console && console.log("Error: " + e ) );
                        }
                    }

                    if(msg.text.length >= 16) {
                        str = msg.text;
                        if( cursor_location != -1 )
                            str = str.replaceAt(cursor_location, "<span class='cursor_location'>" + str[cursor_location] + "</span>");

                        lines[0] = str.substring(0, 16);
                        lines[1] = str.substring(16);
                    }
                    else {
                        str = msg.text;
                        if( cursor_location != -1 )
                            str = str.replaceAt(cursor_location, "<span class='cursor_location'>" + str[cursor_location] + "</span>");
                        lines[0] = str;
                    }

                    if( armed )
                    {
                        $('#status-image1').attr("src", ledImages[0]);
                    }
                    else
                    {
                        $('#status-image1').attr("src", ledImages[1]);
                    }
                    if( ready )
                    {
                        $('#status-image2').attr("src", ledImages[2]);
                    }
                    else
                    {
                        $('#status-image2').attr("src", ledImages[1]);
                    }
                    if( lines[0] != '' )
                    {
                        $('#keypad-line1').html(lines[0]);
                        $('#keypad-line1').css("color", "black");

                        //hackery to get page to stop shifting when only 1 line of text present
                        if( lines[1].match(/ /g).length == 16 )
                            lines[1] = '';
                        if( lines[1].length > 0 )
                        {
                            $('#keypad-line2').css("color", "black");
                            $('#keypad-line2').css("visibility", "visible");
                            $('#keypad-line2').html(lines[1]);
                        }
                        else
                        {
                            $('#keypad-line2').css("color", "white");
                            $('#keypad-line2').css("visibility", "hidden");
                            $('#keypad-line2').html('---');
                        }
                    }

                    if( chime )
                    {
                        $('#chime-image1').attr("src", "{{ url_for('static', filename='img/chime.png') }}" );
                    }
                    else
                    {
                        $('#chime-image1').attr("src", "{{ url_for('static', filename='img/chime-off.png') }}" );
                    }

                }
                if( msg.message_type == 'rfx') {
                    if( msg.battery == true) {
                        str = msg.serial_number + ' Low Battery';
                        $('#keypad-line2').css("color", "black");
                        $('#keypad-line2').css("visibility", "visible");
                        $('#keypad-line2').html(str);
                    }
                }
            });

//lets make the buttons animate when we use keyboard
            $(document).keyup(function(event) {
                var shiftKey = event.shiftKey;
                var charCode = (typeof event.which == "number") ? event.which : event.keyCode;
                var realCharCode = String.fromCharCode(charCode);
//F1-F4
                if( charCode == 112 )
                    $('#button-F1').trigger('mouseup');
                if( charCode == 113 )
                    $('#button-F2').trigger('mouseup');
                if( charCode == 114 )
                    $('#button-F3').trigger('mouseup');
                if( charCode == 115 )
                    $('#button-F4').trigger('mouseup');

//the rest
                if( charCode == 8 || charCode == 9 || charCode == 46 || charCode == 37 || charCode == 39 || (charCode >= 48 && charCode <= 57) || (charCode >= 96 && charCode <= 105 ))
                {
                    if( shiftKey )
                    {
                        if(charCode == 56)
                        {
                            $('#button-star').trigger('mouseup');
                        }
                        if(charCode == 51)
                        {
                            $('#button-pound').trigger('mouseup');
                        }
                    }
                    else
                    {
                        $('#button-' + realCharCode).trigger('mouseup');
                    }
                }

            });
            $(document).keydown(function(event) {
                var shiftKey = event.shiftKey;
                var charCode = (typeof event.which == "number") ? event.which : event.keyCode;
                var realCharCode = String.fromCharCode(charCode);
//F1-F4
                if( charCode == 112 )
                {
                    $('#button-F1').trigger('mousedown');
                }
                if( charCode == 113 )
                {
                    $('#button-F2').trigger('mousedown');
                }
                if( charCode == 114 )
                {
                    $('#button-F3').trigger('mousedown');
                }
                if( charCode == 115 )
                {
                    $('#button-F4').trigger('mousedown');
                }
//the rest
                if( charCode == 8 || charCode == 9 || charCode == 46 || charCode == 37 || charCode == 39 || (charCode >= 48 && charCode <= 57) || (charCode >= 96 && charCode <= 105 ))
                {
                    if( shiftKey )
                    {
                        if(charCode == 56)
                        {
                            $('#button-star').trigger('mousedown');
                        }
                        if(charCode == 51)
                        {
                            $('#button-pound').trigger('mousedown');
                        }
                    }
                    else
                    {
                        $('#button-' + realCharCode).trigger('mousedown');
                    }
                }
            });

//bind our events to our buttons
            bindButtonEvents('#button-1', '1', buttonImageListSmall[2], buttonImageListLarge[2], buttonImageListSmall[3], buttonImageListLarge[3] );
            bindButtonEvents('#button-2', '2', buttonImageListSmall[4], buttonImageListLarge[4], buttonImageListSmall[5], buttonImageListLarge[5] );
            bindButtonEvents('#button-3', '3', buttonImageListSmall[6], buttonImageListLarge[6], buttonImageListSmall[7], buttonImageListLarge[7] );
            bindButtonEvents('#button-4', '4', buttonImageListSmall[8], buttonImageListLarge[8], buttonImageListSmall[9], buttonImageListLarge[9] );
            bindButtonEvents('#button-5', '5', buttonImageListSmall[10], buttonImageListLarge[10], buttonImageListSmall[11], buttonImageListLarge[11] );
            bindButtonEvents('#button-6', '6', buttonImageListSmall[12], buttonImageListLarge[12], buttonImageListSmall[13], buttonImageListLarge[13] );
            bindButtonEvents('#button-7', '7', buttonImageListSmall[14], buttonImageListLarge[14], buttonImageListSmall[15], buttonImageListLarge[15] );
            bindButtonEvents('#button-8', '8', buttonImageListSmall[16], buttonImageListLarge[16], buttonImageListSmall[17], buttonImageListLarge[17] );
            bindButtonEvents('#button-9', '9', buttonImageListSmall[18], buttonImageListLarge[18], buttonImageListSmall[19], buttonImageListLarge[19] );
            bindButtonEvents('#button-0', '0', buttonImageListSmall[0], buttonImageListLarge[0], buttonImageListSmall[1], buttonImageListLarge[1] );
            bindButtonEvents('#button-star', '*', buttonImageListSmall[20], buttonImageListLarge[20], buttonImageListSmall[21], buttonImageListLarge[21] );
            bindButtonEvents('#button-pound', '#', buttonImageListSmall[22], buttonImageListLarge[22], buttonImageListSmall[23], buttonImageListLarge[23] );
//custom buttons
            {% if buttons %}
                $("#exit").on('mousedown', function() {
                    $('#dialog').dialog("close");
                });
                $("#exit").on('touchstart', function() {
                    $('#dialog').dialog("close");
                });

                {% for button in buttons %}
                    $("#custom_{{button.button_id}}").on('mousedown', function() {
                        var code = '{{button.code}}';
                        if( !tablet && !mobile )
                            decoder.emit('keypress', String(code));
                        $('#dialog').dialog("close");
                    });
                    $("#custom_{{button.button_id}}").on('touchend', function() {
                        var code = '{{button.code}}';
                        decoder.emit('keypress', String(code));
                        $('#dialog').dialog("close");
                    });
                {% endfor %}

                if( !tablet && !mobile )
                {
                    $('#custom_buttons').click(function() {
                        $('#dialog').dialog({
                            modal: true,
                            minWidth: 650,
                            maxWidth: 650,
                            position: { my: "center", at: "bottom", of: $('#button-0') },
                        });
                    });
                }
                else
                {
                    if( mobile && !isiPhone )
                    {
                        $('#custom_buttons').on('touchstart', function() {
                            $('#keypad-buttons').hide();
                            $('#dialog').dialog({
                                modal: true,
                                minWidth: 200,
                                position: { my: "center", at: "center", of: window },
                                close: function() {
                                    $('#keypad-buttons').show();
                                }
                            });
                        });
                    }
                    if( mobile && isiPhone )
                    {
                        $('#custom_buttons').on('touchstart', function() {
                            $('#keypad-buttons').hide();
                            $('#dialog').dialog({
                                modal: true,
                                minWidth: 400,
                                position: { my: "center", at: "center", of: window },
                                close: function() {
                                    $('#keypad-buttons').show();
                                }
                            });
                        });
                    }
                    if( tablet )
                    {
                        $('#custom_buttons').on('touchstart', function() {
                            $('#dialog').dialog({
                                modal: true,
                                minWidth: 725,
                                position: { my: "center", at: "bottom", of: window },
                            });
                        });
                    }
                }
            {% endif %}

            $('#button-F1').on('mousedown', function() {
                $(this).attr("src", special_image_defaults_on[{{special_buttons['special_1']}}]);
                checkConfirm({{special_buttons['special_1']}}, "{{special_buttons['special_1_key']}}");
            });
            $('#button-F1').on('mouseup', function() {
                $(this).attr("src", special_image_defaults[{{special_buttons['special_1']}}]);
            });
            $('#button-F2').on('mousedown', function() {
                $(this).attr("src", special_image_defaults_on[{{special_buttons['special_2']}}]);
                checkConfirm({{special_buttons['special_2']}}, "{{special_buttons['special_2_key']}}");
            });
            $('#button-F2').on('mouseup', function() {
                $(this).attr("src", special_image_defaults[{{special_buttons['special_2']}}]);
            });
            $('#button-F3').on('mousedown', function() {
                $(this).attr("src", special_image_defaults_on[{{special_buttons['special_3']}}]);
                checkConfirm({{special_buttons['special_3']}}, "{{special_buttons['special_3_key']}}");
            });
            $('#button-F3').on('mouseup', function() {
                $(this).attr("src", special_image_defaults[{{special_buttons['special_3']}}]);
            });
            $('#button-F4').on('mousedown', function() {
                $(this).attr("src", special_image_defaults_on[{{special_buttons['special_4']}}]);
                checkConfirm({{special_buttons['special_4']}},"{{special_buttons['special_4_key']}}");
            });
            $('#button-F4').on('mouseup', function() {
                $(this).attr("src", special_image_defaults[{{special_buttons['special_4']}}]);
            });

            if( isiPad || isiPhone )
            {
                $('#mute-row').css('display', 'none');
            }
            $('#check-mute').change(function() {
                var toggled = $(this).prop('checked');

                if( toggled == false)
                    mute = 1;
                else
                    mute = 0;

                if( storageSupported() )
                    localStorage.setItem("mute", mute);
            });
        })
    </script>
