<script type="text/javascript">
    var timeoutVar;

    function poll_app_restarted()
    {
        $.ajax({
            url: "{{ url_for('update.checkavailable') }}",
            type: "GET",
            timeout: 3000,
            statusCode: {
                502: function() {
                    $('#app_running').html('<img src="{{ url_for("static", filename="img/spinner.gif") }}"> Application is restarting...');
                    timeoutVar = setTimeout(function() { poll_app_restarted(); }, 5000);
                }
            },
            success: function(data) {
                var jsondata = JSON.parse(data);

                if( jsondata['status'] )
                {
                    if( jsondata['status'] == 'PASS' )
                    {
                        clearTimeout(timeoutVar);
                        window.location.reload();
                    }
                }
            },
            complete: function(xhr, status) {
                if (status === 'timeout')
                {
                    console.log('timed out.. requesting again..');
                    timeoutVar = setTimeout(function() { poll_app_restarted(); }, 1000);
                }
            },
        });
    }

    function build_update_button(component, enabled) {
        if (enabled === true) {
            $('#' + component + '-update-submit').show();
        }

        $('#' + component + '-update-submit').click(function() {
            $('#' + component + '-status').html('');
            $('#' + component + '-update-submit').hide();
            $('#' + component + '-update-anim').show();

            $.ajax({
                url: "{{ url_for('update.update') }}",
                type: 'POST',
                data: JSON.stringify({ 'component': component }),
                contentType: 'application/json;charset=UTF-8',
                success: function(data, status, xhr) {
                    var jsondata = JSON.parse(data);

                    if (jsondata[component]['status'] == 'PASS')
                    {
                        $('#' + component + '-status').html('<span style="color:green">&#10004;</span>');

                        if (jsondata[component]['restart_required'] === true)
                        {
                            $('#' + component + '-restart-submit').show();
                        }
                    }
                    else
                    {
                        $('#' + component + '-status').html('<span style="color:red">&#10008;</span>');
                        $('#' + component + '-update-submit').show();
                    }
                },
                complete: function() {
                    $('#' + component + '-update-anim').hide();
                }
            });

            return false;
        });

        $('#' + component + '-restart-submit').click(function() {
            $('#' + component + '-status').html('');
            $('#' + component + '-restart-submit').hide();
            $('#' + component + '-update-anim').show();

            $.ajax({
                url: "{{ url_for('update.restart') }}",
                type: 'POST',
                data: JSON.stringify({ 'component': component }),
                contentType: 'application/json;charset=UTF-8',
                complete: function() {
                    decoder.disconnect();
                    $('#app_running').html('<img src="{{ url_for("static", filename="img/spinner.gif") }}"> Application is restarting...');
                    timeoutVar = setTimeout(function() { poll_app_restarted(); }, 5000);
                }
            });

            return false;
        });
    }

    $('body').ready(function() {
    {% for component, (needs_update, branch, revision, new_revision, status, project_url) in updates.iteritems() %}
        build_update_button('{{ component }}', '{{ needs_update }}' === 'True');
    {% endfor %}
    });
</script>
