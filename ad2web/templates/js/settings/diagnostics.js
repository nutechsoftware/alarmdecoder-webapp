{% include 'js/setup/enrollment.js' %}
<script type="text/javascript">
fullMessages = [];

    $(document).ready(function() {
        var allmodsfound = 1;
        $.fn.spin.presets.flower = {
            lines: 13,
            length: 30,
            width: 10,
            radius: 30,
            className: 'spinner',
        }

        $('#test_modules').on('click', function() {
            $('#import_list_detail').html('');
            $('#loading').show(); 
            $('#loading').spin('flower');

            //get list of modules, then test each module to see if present on system
            $.ajax({
                url: "{{url_for('settings.get_system_imports')}}",
                dataType: 'json',
                success: function(data) {
                    var i = 0;
                    $.each(data, function(index, element) {

                        if(element.found == 1 )
                        {
                            $('#import_list_detail').append("<span class='found'><font color='green'>" + element.modname + "</font></span>");
                        }
                        else
                        {
                            allmodsfound = 0;
                            $('#import_list_detail').append("<span class='missing'><font color='red'>" + element.modname + "</font></span>");
                        }

                        if( i != 0 && i % 16 == 0 )
                        {
                            $('#import_list_detail').append("<br/>");
                        }
                        else
                        {
                            $('#import_list_detail').append(" ");
                        }

                        i++;
                    });
                    $('#loading').stop();
                    $('#loading').hide();
                },
                complete: function(data) {
                    if($('#chk_showall').is(':checked'))
                        $('.found').show();
                    else
                        $('.found').hide();

                    if( allmodsfound == 1 )
                        $('#import_list_detail').html('<font color="green">ALL MODULES FOUND</font>');
                },
            });
        });

        //show all modules or just missing modules
        $('#chk_showall').change(function() {
            if(this.checked)
            {
                $('.found').show();
            }
            else
            {
                $('.found').hide();
            }
        });

        //device testing
        PubSub.subscribe('test', function(type, msg) {

            result_text = {
                'PASS': '<span style="color:green">&#10004;</span>',
                'FAIL': '<span style="color:red">&#10008;</span>',
                'TIMEOUT': '<span style="color:orange">&#9888;</span>'
            };
            test_results = $('table#test_results tr#test-' + msg.test);
            $(test_results).children('td:eq(1)').html(result_text[msg.results]);
            $(test_results).children('td:eq(2)').html(msg.details);

        });

        PubSub.subscribe('message', function(type, msg) {
            if( msg.message_type == "aui" )
            {
                value = msg.value.trim();
                prefix = getAUIPrefix(value);

                if( state == states['queryLog'] )
                {
                    numLogEntries = parseAUIMessage(prefix, value);
                    state = states['queryLogDone'];
                    if( !isNaN(numLogEntries) )
                    {
                        $('#numDevices').html('Number of Event Log Entries: ' + numLogEntries + '<br/>');
                        $('#dialog').dialog({ width: 600, height: 500, close: function() { $('#numDevices').text('');  $('#textLogEntries').val(''); state = state['queryLogDetailsDone']; countLogEntries = 0;}});
                        state = states['queryLogDetails'];
                        checkDeviceLogs(numLogEntries);
                    }
                }
                if( state == states['queryLogDetails'] )
                {
                    logMessage = parseAUIMessage(prefix, value);
                    fullMessage = countLogEntries + ': ' + logMessage + '\r\n';

                    if( !asciiToHex(logMessage).startsWith("05") )
                    {
                        if( !in_array(fullMessages, fullMessage) )
                        {
                            $('#textLogEntries').append(fullMessage);
                            fullMessages.push(fullMessage);
                        }
                    }
                    if( countLogEntries > parseInt(numLogEntries) )
                        state = states['queryLogDetailsDone'];
                }
                if( state == states['queryLogDone'] && isNaN(numLogEntries) )
                {
                    state = states['unsupported'];
                    alert('It would appear your particular honeywell panel does not support this');
                }
            }
        });

        $('#test_decoder').on('click', function() {
            $('#decoder_detail').show();
            var spinner = '<img src="{{url_for('static', filename='img/spinner.gif')}}"/>';
            $('table#test_results tr#test-open').children('td:eq(1)').html(spinner);
            $('table#test_results tr#test-open').children('td:eq(2)').html('');
            $('table#test_results tr#test-config').children('td:eq(1)').html(spinner);
            $('table#test_results tr#test-config').children('td:eq(2)').html('');
            $('table#test_results tr#test-send').children('td:eq(1)').html(spinner);
            $('table#test_results tr#test-send').children('td:eq(2)').html('');
            $('table#test_results tr#test-recv').children('td:eq(1)').html(spinner);
            $('table#test_results tr#test-recv').children('td:eq(2)').html('');
            
            decoder.emit('test');
        });
        $('#startEventQuery').on('click', function() {
            state = states['queryLog'];
            queryLog();
        });
        $('#btnCopy').on('click', function() {
            $('#textLogEntries').select();
            document.execCommand('copy');
        });
    });
</script>
