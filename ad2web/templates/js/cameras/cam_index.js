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

        $(document).ready(function() {
            //detect mobile and tablet
            mobile = isMobile();
            tablet = isTablet();

            $(function() {
                FastClick.attach(document.body);
            });
//tab our camera interface
            $('#camera_tabs').tabs({
//remember which tab we were on
                active: localStorage.getItem("currentCamTabIndex"),
                activate: function(event, ui) {
                    localStorage.setItem("currentCamTabIndex", $("#camera_tabs").tabs("option", "active"));
                }
            });
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
                            position: { my: "center", at: "bottom", of: $('#camera_tabs') },
                        });
                    });
                }
                else
                {
                    if( mobile && !isiPhone )
                    {
                        $('#custom_buttons').on('touchstart', function() {
                            $('#dialog').dialog({
                                modal: true,
                                minWidth: 200,
                                position: { my: "center", at: "center", of: window },
                                close: function() {
                                }
                            });
                        });
                    }
                    if( mobile && isiPhone )
                    {
                        $('#custom_buttons').on('touchstart', function() {
                            $('#dialog').dialog({
                                modal: true,
                                minWidth: 400,
                                position: { my: "center", at: "center", of: window },
                                close: function() {
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

            window.setInterval(function() {
                {% for camera in camera_list %}
                    $("#cam_image{{camera.id}}").each(function() {
                        var jqt = $(this);
                        var src = jqt.attr('src');
                        var newsrc = '';

                        if( src.indexOf('?') != -1 )
                            newsrc = src.substr(0, src.indexOf('?'));
                        else
                            newsrc = src;
                        newsrc += '?_ts=' + new Date().getTime();
                        jqt.attr('src', newsrc);
                    });
                {% endfor %}
            }, 250);
        });

    </script>
