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

    $('#restartbutton').on('click', function() {
        $.confirm({
            content: "Are you sure?",
            title: "Restart webapp",
            confirm: function(button) {
              $.ajax({
                  url: "{{ url_for('update.restart') }}",
                  type: 'POST',
                  data: JSON.stringify({ 'foo': 0 }),
                  contentType: 'application/json;charset=UTF-8',
                  complete: function() {
                      decoder.disconnect();
                      $('#app_running').html('<img src="{{ url_for("static", filename="img/spinner.gif") }}"> Application is restarting...');
                      timeoutVar = setTimeout(function() { poll_app_restarted(); }, 5000);
                  }
              });
              return false;
            },
            cancel: function(button) {
            },
            confirmButton: "Yes",
            cancelButton: "No",
            post: false,
        });
    });

</script>
