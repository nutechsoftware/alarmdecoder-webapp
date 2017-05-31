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
        $('#buttons-table').dataTable({
            responsive: true,
            stateSave: true,
            stateDuration: 60 * 60 * 24,
            pagingType: "full_numbers",
            language: {
                info: "_START_ to _END_ of _TOTAL_",
                infoEmpty: "No Results",
                emptyTable: " ",
                infoFiltered: "",
            },
            initComplete: function() {
                $('#loading').stop();
                $('#loading').hide();
                $('#datatable').show();
            },
        });
    });
</script>
