<script type="text/javascript">
    var timeout;
    function get_log_data(num_lines)
    {
        $.ajax({
            type: "GET",
            dataType: "json",
            url: '/log/alarmdecoder/get_data/' + num_lines,
            success: function(data) {
                var newline = '\r\n';
                $('#log_data').val('');
                for( var i = 0; i < data.length; i++ )
                {
                    text = $.trim(data[i]);
                    $('#log_data').val( $('#log_data').val() + text + newline );
                }
            },
        });
        timeout = setTimeout(function(){ get_log_data(num_lines); }, 10000);
    }

    $(document).ready(function() {
        var num_lines = $('#num_lines').val();
        get_log_data(num_lines);

        $('#num_lines').change(function() {
            window.clearTimeout(timeout);
            num_lines = $('#num_lines').val();
            get_log_data(num_lines);
        });

        $('#log_data').focus(function() {
            var $this = $(this);
            $this.select();

            window.setTimeout(function() {
                $this.select();
            }, 1);
            function mouseUpHandler() {
                $this.off("mouseup", mouseUpHandler);
                return false;
            }

            $this.mouseup(mouseUpHandler);
        });
        $('#stop_refresh').click(function() {
            var isChecked = $('#stop_refresh').prop('checked') ? true : false;

            if( isChecked )
                window.clearTimeout(timeout);
            else
            {
                num_lines = $('#num_lines').val();
                get_log_data(num_lines);
            }
        });
    });
</script>
