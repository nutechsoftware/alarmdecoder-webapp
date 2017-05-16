   <script type="text/javascript">
        $(document).ready(function() {
            $.fn.dataTableExt.oPagination.iFullNumbersShowPages = 3;
            $.fn.spin.presets.flower = {
                lines: 13,
                length: 30,
                width: 10,
                radius: 30,
                className: 'spinner',
            }
            $('#loading').spin('flower');

            var oTable = $('#history-table').dataTable({
                "bStateSave": true,
                "iCookieDuration": 60*60*24,
                "sPaginationType": "full_numbers",
                "oLanguage": {
                    "sInfoFiltered": "",
                    "sInfo": "_START_ to _END_ of _TOTAL_",
                    "sInfoEmpty": "No Results",
                    "sInfoThousands": "",
                    "sEmptyTable": " ",
                },
                "fnInitComplete": function() {
                    $('#loading').stop();
                    $('#loading').hide();
                    $('#datatable').show();
                    this.fnAdjustColumnSizing();
                },
            });
        });
    </script>
