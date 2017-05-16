<script type="text/javascript">
    $(document).ready(function() {
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

        decoder.emit('test');
    });
</script>
