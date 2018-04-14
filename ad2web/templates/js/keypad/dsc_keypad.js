    <script type="text/javascript">
        String.prototype.replaceAt = function(index, str) {
            return this.substr(0, index) + str + this.substr(index+1);
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
            "{{ url_for('static', filename='img/dsc-0-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-0-large.png') }}",
            "{{ url_for('static', filename='img/dsc-1-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-1-large.png') }}",
            "{{ url_for('static', filename='img/dsc-2-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-2-large.png') }}",
            "{{ url_for('static', filename='img/dsc-3-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-3-large.png') }}",
            "{{ url_for('static', filename='img/dsc-4-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-4-large.png') }}",
            "{{ url_for('static', filename='img/dsc-5-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-5-large.png') }}",
            "{{ url_for('static', filename='img/dsc-6-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-6-large.png') }}",
            "{{ url_for('static', filename='img/dsc-7-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-7-large.png') }}",
            "{{ url_for('static', filename='img/dsc-8-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-8-large.png') }}",
            "{{ url_for('static', filename='img/dsc-9-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-9-large.png') }}",
            "{{ url_for('static', filename='img/dsc-star-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-star-large.png') }}",
            "{{ url_for('static', filename='img/dsc-pound-large-on.png') }}",
            "{{ url_for('static', filename='img/dsc-pound-large.png') }}",
            "{{ url_for('static', filename='img/f1-fire-on.png') }}",
            "{{ url_for('static', filename='img/f1-fire.png') }}",
            "{{ url_for('static', filename='img/f2-police-on.png') }}",
            "{{ url_for('static', filename='img/f2-police.png') }}",
            "{{ url_for('static', filename='img/f3-medical-on.png') }}",
            "{{ url_for('static', filename='img/f3-medical.png') }}",
            "{{ url_for('static', filename='img/f4-led-text-on.png') }}",
            "{{ url_for('static', filename='img/f4-led-text.png') }}",
            "{{ url_for('static', filename='img/dsc-stay.png') }}",
            "{{ url_for('static', filename='img/dsc-away.png') }}",
            "{{ url_for('static', filename='img/dsc-chime.png') }}",
            "{{ url_for('static', filename='img/dsc-reset.png') }}",
            "{{ url_for('static', filename='img/dsc-cursor-left.png') }}",
            "{{ url_for('static', filename='img/dsc-cursor-right.png') }}"
        ];

        var buttonImageListSmall = [
            "{{ url_for('static', filename='img/dsc-0-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-0-small.png') }}",
            "{{ url_for('static', filename='img/dsc-1-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-1-small.png') }}",
            "{{ url_for('static', filename='img/dsc-2-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-2-small.png') }}",
            "{{ url_for('static', filename='img/dsc-3-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-3-small.png') }}",
            "{{ url_for('static', filename='img/dsc-4-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-4-small.png') }}",
            "{{ url_for('static', filename='img/dsc-5-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-5-small.png') }}",
            "{{ url_for('static', filename='img/dsc-6-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-6-small.png') }}",
            "{{ url_for('static', filename='img/dsc-7-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-7-small.png') }}",
            "{{ url_for('static', filename='img/dsc-8-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-8-small.png') }}",
            "{{ url_for('static', filename='img/dsc-9-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-9-small.png') }}",
            "{{ url_for('static', filename='img/dsc-star-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-star-small.png') }}",
            "{{ url_for('static', filename='img/dsc-pound-small-on.png') }}",
            "{{ url_for('static', filename='img/dsc-pound-small.png') }}",
            "{{ url_for('static', filename='img/f1-fire-small-on.png') }}",
            "{{ url_for('static', filename='img/f1-fire-small.png') }}",
            "{{ url_for('static', filename='img/f2-police-small-on.png') }}",
            "{{ url_for('static', filename='img/f2-police-small.png') }}",
            "{{ url_for('static', filename='img/f3-medical-small-on.png') }}",
            "{{ url_for('static', filename='img/f3-medical-small.png') }}",
            "{{ url_for('static', filename='img/f4-led-text-small-on.png') }}",
            "{{ url_for('static', filename='img/f4-led-text-small.png') }}",
            "{{ url_for('static', filename='img/dsc-stay.png') }}",
            "{{ url_for('static', filename='img/dsc-away.png') }}",
            "{{ url_for('static', filename='img/dsc-chime.png') }}",
            "{{ url_for('static', filename='img/dsc-reset.png') }}",
            "{{ url_for('static', filename='img/dsc-cursor-left.png') }}",
            "{{ url_for('static', filename='img/dsc-cursor-right.png') }}"
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
            "{{ url_for('static', filename='img/s5-off.png') }}",
            "{{ url_for('static', filename='img/s5-on.png') }}",
            "{{ url_for('static', filename='img/s6-off.png') }}",
            "{{ url_for('static', filename='img/s6-on.png') }}",
            "{{ url_for('static', filename='img/s7-off.png') }}",
            "{{ url_for('static', filename='img/s7-on.png') }}",
            "{{ url_for('static', filename='img/s8-off.png') }}",
            "{{ url_for('static', filename='img/s8-on.png') }}",
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
            var keypadline2 = document.getElementById("keypad-line2");
            keypadline1.style.fontSize = "25px";
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

        function checkConfirm(special_button_id, special_button_value, element)
        {
            if( special_button_id == keypadSpecials.SPECIAL_CUSTOM )
            {
                $.confirm({
                    content: "Are you sure you want to send " + special_button_value + "?",
                    title: "Custom Special Button",
                    confirm: function(button) {
                        add_flash_message("Custom Command " + special_button_value + " Sent", "error");
                        decoder.emit('keypress', special_button_value);
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
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
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
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
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
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
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
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
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });

            }

            if( special_button_id == keypadSpecials.STAY )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Confirmation required",
                    confirm: function(button) {
                        add_flash_message("Notification sent.", "error");
                        decoder.emit('keypress', 's');
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.AWAY )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Confirmation required",
                    confirm: function(button) {
                        add_flash_message("Notification sent.", "error");
                        decoder.emit('keypress', 'a');
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.CHIME )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Confirmation required",
                    confirm: function(button) {
                        add_flash_message("Notification sent.", "error");
                        decoder.emit('keypress', 'c');
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.RESET )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Confirmation required",
                    confirm: function(button) {
                        add_flash_message("Notification sent.", "error");
                        decoder.emit('keypress', 'r');
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
                    },
                    confirmButton: "Yes I am",
                    cancelButton: "No",
                    post: false,
                });
            }

            if( special_button_id == keypadSpecials.EXIT )
            {
                $.confirm({
                    content: "Are you sure?",
                    title: "Confirmation required",
                    confirm: function(button) {
                        add_flash_message("Notification sent.", "error");
                        decoder.emit('keypress', 'e');
                        element.trigger('mouseup');
                    },
                    cancel: function(button) {
                        element.trigger('mouseup');
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

            preloadImages(buttonImageListLarge);
            preloadImages(specialImageList);

            special_image_defaults = { 0: buttonImageListSmall[25], 1: buttonImageListSmall[27], 2: buttonImageListSmall[29], 3: buttonImageListSmall[31], 6: buttonImageListSmall[32], 7: buttonImageListSmall[33], 8: buttonImageListSmall[34], 9: buttonImageListSmall[35], 10: specialImageList[0] };

            special_image_defaults_on = { 0: buttonImageListSmall[24], 1: buttonImageListSmall[26], 2: buttonImageListSmall[28], 3: buttonImageListSmall[31], 6: buttonImageListSmall[32], 7: buttonImageListSmall[33], 8: buttonImageListSmall[34], 9: buttonImageListSmall[35], 10: specialImageList[1] };


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

            if( {{special_buttons['special_1']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-F1').attr("src", special_image_defaults[{{special_buttons['special_1']}}]);
            else
                $('#button-F1').attr("src", specialImageList[0]);

            if( {{special_buttons['special_2']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-F2').attr("src", special_image_defaults[{{special_buttons['special_2']}}]);
            else
                $('#button-F2').attr("src", specialImageList[2]);

            if( {{special_buttons['special_3']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-F3').attr("src", special_image_defaults[{{special_buttons['special_3']}}]);
            else
                $('#button-F3').attr("src", specialImageList[4] );

            if( {{special_buttons['special_4']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-stay').attr("src", special_image_defaults[{{special_buttons['special_4']}}]);
            else
                $('#button-stay').attr("src", specialImageList[6]);

            if( {{special_buttons['special_5']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-away').attr("src", special_image_defaults[{{special_buttons['special_5']}}]);
            else
                $('#button-away').attr("src", specialImageList[8]);

            if( {{special_buttons['special_6']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-chime').attr("src", special_image_defaults[{{special_buttons['special_6']}}]);
            else
                $('#button-chime').attr("src", specialImageList[10]);

            if( {{special_buttons['special_7']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-reset').attr("src", special_image_defaults[{{special_buttons['special_7']}}]);
            else
                $('#button-reset').attr("src", specialImageList[12]);

            if( {{special_buttons['special_8']}} != keypadSpecials.SPECIAL_CUSTOM )
                $('#button-exit').attr("src", special_image_defaults[{{special_buttons['special_8']}}]);
            else
                $('#button-exit').attr("src", specialImageList[14]);

            $('#button-left').attr("src", buttonImageListSmall[36]);
            $('#button-right').attr("src", buttonImageListSmall[37]);

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
                        $('#chime-image1').attr("src", "{{ url_for('static', filename='img/chime.png') }}");
                    }
                    else
                    {
                        $('#chime-image1').attr("src", "{{ url_for('static', filename='img/chime-off.png') }}" );
                    }
                }
            });

//lets make the buttons animate when we use keyboard
            $(document).keyup(function(event) {
                var shiftKey = event.shiftKey;
                var charCode = (typeof event.which == "number") ? event.which : event.keyCode;
                var realCharCode = String.fromCharCode(charCode);
//DSC Stay/Away/Chime/Reset/Exit
                if( charCode == 83 && !event.ctrlKey)
                {
                    $('#button-stay').trigger('mouseup');
                }
                if( charCode == 65 && !event.ctrlKey)
                {
                    $('#button-away').trigger('mouseup');
                }
                if( charCode == 67 && !event.ctrlKey)
                {
                    $('#button-chime').trigger('mouseup');
                }
                if( charCode == 82 && !event.ctrlKey)
                {
                    $('#button-reset').trigger('mouseup');
                }
                if( charCode == 69 && !event.ctrlKey )
                {
                    $('#button-exit').trigger('mouseup');
                }

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
//DSC Stay/Away/Chime/Reset/Exit
                if( charCode == 83 && !event.ctrlKey)
                {
                    $('#button-stay').trigger('mousedown');
                }
                if( charCode == 65 && !event.ctrlKey)
                {
                    $('#button-away').trigger('mousedown');
                }
                if( charCode == 67 && !event.ctrlKey)
                {
                    $('#button-chime').trigger('mousedown');
                }
                if( charCode == 82 && !event.ctrlKey)
                {
                    $('#button-reset').trigger('mousedown');
                }
                if( charCode == 69 && !event.ctrlKey )
                {
                    $('#button-exit').trigger('mousedown');
                }
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
            bindButtonEvents('#button-left',  '<', buttonImageListSmall[36], buttonImageListSmall[36], buttonImageListSmall[36], buttonImageListSmall[36]);
            bindButtonEvents('#button-right', '>', buttonImageListSmall[37], buttonImageListSmall[37], buttonImageListSmall[37], buttonImageListSmall[37]);
//custom buttons

                if( !tablet && !mobile )
                {
                    $('#special_buttons').click(function() {
                        $('#special-dialog').dialog({
                            modal: true,
                            minWidth: 650,
                            maxWidth: 650,
                            position: { my: "center", at: "bottom", of: $('#keypad-row') },
                        });
                    });
                }
                else
                {
                    if( mobile && !isiPhone )
                    {
                        $('#special_buttons').on('touchend', function() {
                            $('#keypad-buttons').hide();
                            $('#special-dialog').dialog({
                                modal: true,
                                minWidth: 200,
                                position: { my: "center", at: "center", of: window },
                                close: function() {
                                    $('#keypad-buttons').show();
                                },
                            });
                        });
                    }
                    if( mobile && isiPhone )
                    {
                        $('#special_buttons').on('touchstart', function() {
                            $('#keypad-buttons').hide();
                            $('#special-dialog').dialog({
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
                        $('#special_buttons').on('touchstart', function() {
                            $('#special-dialog').dialog({
                                modal: true,
                                minWidth: 725,
                                position: { my: "center", at: "bottom", of: window },
                            });
                        });
                    }
                }
            {% if buttons %}
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
                            position: { my: "center", at: "bottom", of: $('#keypad-row') },
                        });
                    });
                }
                else
                {
                    if( mobile && !isiPhone )
                    {
                        $('#custom_buttons').on('touchend', function() {
                            $('#keypad-buttons').hide();
                            $('#dialog').dialog({
                                modal: true,
                                minWidth: 200,
                                position: { my: "center", at: "center", of: window },
                                close: function() {
                                    $('#keypad-buttons').show();
                                },
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
                if( {{special_buttons['special_1']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_1']}}]);
                else
                    $(this).attr("src", specialImageList[1]);

                var key = "{{special_buttons['special_1_key']}}";
                checkConfirm({{special_buttons['special_1']}}, key, $('#button-F1'));
            });
            $('#button-F1').on('mouseup', function() {
                if( {{special_buttons['special_1']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_1']}}]);
                else
                    $(this).attr("src", specialImageList[0]);

            });
            $('#button-F2').on('mousedown', function() {
                if( {{special_buttons['special_2']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_2']}}]);
                else
                    $(this).attr("src", specialImageList[3] );

                var key = "{{special_buttons['special_2_key']}}";
                checkConfirm({{special_buttons['special_2']}}, key, $('#button-F2'));
            });
            $('#button-F2').on('mouseup', function() {
                if( {{special_buttons['special_2']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_2']}}]);
                else
                    $(this).attr("src", specialImageList[2]);

            });
            $('#button-F3').on('mousedown', function() {
                if( {{special_buttons['special_3']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_3']}}]);
                else
                    $(this).attr("src", specialImageList[5]);

                var key = "{{special_buttons['special_3_key']}}";
                checkConfirm({{special_buttons['special_3']}}, key, $('#button-F3'));
            });
            $('#button-F3').on('mouseup', function() {
                if( {{special_buttons['special_3']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_3']}}]);
                else
                    $(this).attr("src", specialImageList[4]);
            });
            $('#button-F4').on('mousedown', function() {
                if( {{special_buttons['special_4']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_4']}}]);
                else
                    $(this).attr("src", specialImageList[7]);

                var key = "{{special_buttons['special_4_key']}}";
                checkConfirm({{special_buttons['special_4']}}, key, $('#button-F4'));
            });
            $('#button-F4').on('mouseup', function() {
                if( {{special_buttons['special_4']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_4']}}]);
                else
                    $(this).attr("src", specialImageList[6] );
            });

            $('#button-stay').on('mousedown', function() {
                if( {{special_buttons['special_4']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_4']}}]);
                else
                    $(this).attr("src", specialImageList[9]);

                var key = "{{special_buttons['special_4_key']}}";
                checkConfirm({{special_buttons['special_4']}}, key, $('#button-stay'));
            });
            $('#button-stay').on('mouseup', function() {
                if( {{special_buttons['special_4']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_4']}}]);
                else
                    $(this).attr("src", specialImageList[8]);
            });
        
            $('#button-away').on('mousedown', function() {
                if( {{special_buttons['special_5']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_5']}}]);
                else
                    $(this).attr("src", specialImageList[11]);

                var key = "{{special_buttons['special_5_key']}}";
                checkConfirm({{special_buttons['special_5']}}, key, $('#button-away'));
            });
            $('#button-away').on('mouseup', function() {
                if( {{special_buttons['special_5']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_5']}}]);
                else
                    $(this).attr("src", specialImageList[10]);
            });

            $('#button-chime').on('mousedown', function() {
                if( {{special_buttons['special_6']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_6']}}]);
                else
                    $(this).attr("src", specialImageList[13]);

                var key = "{{special_buttons['special_6_key']}}";
                checkConfirm({{special_buttons['special_6']}}, key, $('#button-chime'));
            });
            $('#button-chime').on('mouseup', function() {
                if( {{special_buttons['special_6']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_6']}}]);
                else
                    $(this).attr("src", specialImageList[12]);
            });

            $('#button-reset').on('mousedown', function() {
                if( {{special_buttons['special_7']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_7']}}]);
                else
                    $(this).attr("src", specialImageList[15]);

                var key = "{{special_buttons['special_7_key']}}";
                checkConfirm({{special_buttons['special_7']}}, key, $('#button-reset'));
            });
            $('#button-reset').on('mouseup', function() {
                if( {{special_buttons['special_7']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_7']}}]);
                else
                    $(this).attr("src", specialImageList[14]);
            });

            $('#button-exit').on('mousedown', function () {
                if( {{special_buttons['special_8']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults_on[{{special_buttons['special_8']}}]);
                else
                    $(this).attr("src", specialImageList[17]);

                var key = "{{special_buttons['special_8_key']}}";
                checkConfirm({{special_buttons['special_8']}}, key, $('#button-exit'));
            });
            $('#button-exit').on('mouseup', function() {
                if( {{special_buttons['special_8']}} != keypadSpecials.SPECIAL_CUSTOM )
                    $(this).attr("src", special_image_defaults[{{special_buttons['special_8']}}]);
                else
                    $(this).attr("src", specialImageList[16]);
            });

            if( isiPad || isiPhone )
            {
                $('#mute-row').css('display', 'none');
            }
            $('#check-mute').change(function() {
                var toggled = $(this).prop('checked');

                if( toggled == false )
                    mute = 1;
                else
                    mute = 0;

                if( storageSupported() )
                    localStorage.setItem("mute", mute);
            });

        })
    </script>
