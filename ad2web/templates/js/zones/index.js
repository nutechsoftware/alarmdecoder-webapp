{% include 'js/setup/enrollment.js' %}
<script type="text/javascript">
    $(document).ready(function(){
        $.fn.spin.presets.flower = {
            lines: 13,
            length: 30,
            width: 10,
            radius: 30,
            className: 'spinner',
        }
        $('#loading').spin('flower');
        $('#zones-table').DataTable({
            responsive: true,
            stateSave: true,
            stateDuration: 60 * 60 * 24,
            pagingType: "full_numbers",
            language: {
                infoEmpty: "No Results",
                infoFiltered: "",
                emptyTable: " ",
                info: "_START_ to _END_ of _TOTAL_",
            },
            order: [[1, "asc"]],
            initComplete: function() {
                $('#loading').stop();
                $('#loading').hide();
                $('#clear').css('display', 'inline-block');
                $('#datatable').show();
            },
        });
        PubSub.subscribe('message', function(type, msg) {
            if( msg.message_type == "aui" )
            {
                prefix = getAUIPrefix(msg.value);
                value = msg.value.trim();

                if( state == states['getPartitionCount'] )
                {
                    partitionCount = parseAUIMessage(prefix, value);
                    state = states['getPartitionCountDone'];
                    decoder.emit('keypress', "K18\r\n");
                }
                if( state == states['getZoneData'] )
                {
                    zone = parseAUIMessage(prefix, value);
                }
            }
            if( state == states['getZoneDataDone'] )
            {
                if( zones.length > 0 )
                {
                    populateZones(zones);
                }
            }
        });
        if( {{panel_mode}} == 0 )
        {
            setConfigBits();
        }
        $('#importZone').on('click', function() {
            $.confirm({
                content: "This will take a few minutes - this will also delete existing configured zones from the WebApp.<br/>This is not compatible with SE panels or panels without AUI support.  You do not need an AUI keypad, your panel just needs to support one.",
                title: "Scan Alarm for Zones?",
                confirm: function(button) {
                    $('#zone_scanning').spin('flower');
                    $('.progress_label').show();
                    $('#progressbar').show();
                    $('#progressbar').progressbar({
                        change: function() {
                            $('.progress_label').text("Current Progress: " + $('#progressbar').progressbar( "value" ) + "%" );
                        }
                    });
                    if( getZoneData() == false )
                        alert('Unable to get partition Count, likely unsupported');
                },
                cancel: function(button) {
                },
                confirmButton: "Scan",
                cancelButton: "Cancel",
                post: false,
            });
        });
    });
</script>
