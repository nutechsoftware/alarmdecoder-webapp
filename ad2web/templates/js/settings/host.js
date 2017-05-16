<script type="text/javascript">
    function get_ethernet_properties(device)
    {
        //get ethernet device settings based on value of ethernet dropdown
        $.ajax( {
            dataType: "json",
            url: "/settings/get_ethernet_info/" + device,
        }).done( function( data ) {
            $('#network_device_settings').html('');

            var device = data['device'];
            $('#network_device_settings').append('<b>Device: </b>' + device + '<br/>');
            var default_gateway = data['default_gateway'][0];
            $('#network_device_settings').append('<b>Default Gateway: </b>' + default_gateway + '<br/>');
            var mac_address = data['mac_address'][0]['addr'];
            $('#network_device_settings').append('<b>MAC Address: </b>' + mac_address + '<br/>');
            var ipv4 = []
            var ipv6 = []
            for( var i = 0; i < data['ipv4'].length; i++ )
            {
                ipv4.push(data['ipv4'][i]);
            }
            if( data['ipv6'] )
            {
                for( var i = 0; i < data['ipv6'].length; i++ )
                {
                    ipv6.push(data['ipv6'][i]);
                }
            }
            if( ipv4.length > 0 )
            {
                $('#network_device_settings').append('<br/><b>IPV4 Addresses:</b><br/>');
                for( var i = 0; i < ipv4.length; i++)
                {
                    for( var key in ipv4[i] )
                    {
                        $('#network_device_settings').append('&nbsp;&nbsp;&nbsp;&nbsp;<b>' + key + ': </b>' + ipv4[i][key] + '<br/>');
                    }
                }
            }

            if( ipv6.length > 0 )
            {
                $('#network_device_settings').append('<br/><b>IPV6 Addresses:</b><br/>');
                for( var i = 0; i < ipv6.length; i++ )
                {
                    for( var key in ipv6[i] )
                    {
                        $('#network_device_settings').append('&nbsp;&nbsp;&nbsp;&nbsp;<b>' + key + ': </b>' + ipv6[i][key] + '<br/>');
                    }
                }
            }
        });
    }

    $(document).ready(function() {
        createFormTooltip('#ethernet_devices', 'Please select a device.');
        get_ethernet_properties($('#ethernet_devices').val());
        $('#ethernet_devices').on('change', function() {
            var selectedVal = $('#ethernet_devices').val();
            get_ethernet_properties(selectedVal);
        });
    });
</script>
