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

        $('#certificate-table').dataTable({
            "bJQueryUI" : true,
            "bStateSave": true,
            "iCookieDuration": 60*60*24,
            "sPaginationType" : "full_numbers",
            "sDom" : '<"H"lr>t<"F"fip>',
            "oLanguage": {
                "sInfoFiltered": "",
                "sInfo": "_START_ to _END_ of _TOTAL_",
                "sInfoEmpty": "No Results",
                "sEmptyTable": " ",
            },
            "aoColumns": [
                { "sWidth": "16%"},
                { "sWidth": "13%"},
                { "sWidth": "8%" },
                { "sWidth": "8%" },
                null
            ],
            "fnInitComplete": function() {
                $('#loading').stop();
                $('#loading').hide();
                $('#datatable').show();
                this.fnAdjustColumnSizing();
            },
        });
    });
</script>
