    <script type="text/javascript">
        function RenderDateLocal(oObj)
        {
            //parse date from python to format Date object understands
            var match = oObj.match(/^(\d+)-(\d+)-(\d+) (\d+)\:(\d+)\:(\d+)$/);

            var localDate = new Date(match[1], match[2] - 1, match[3], match[4], match[5], match[6]);

            //take care of timezone offset in minutes to hours by negating and then adding to the hours
            var tzo = (localDate.getTimezoneOffset()/60) *-1;
            localDate.setHours(localDate.getHours() + tzo );

            //reformat date for consistency
            var dateStr = localDate.getFullYear() + "-" + (localDate.getMonth() + 1) + "-" + localDate.getDate() + " " + localDate.toLocaleTimeString();
            return dateStr;
        }
        function showHide(bShow)
        {
            if( bShow )
            {
                $('#loading').show();
                $('#loading').spin('flower');
            }
            else
            {
                $('#loading').stop();
                $('#loading').hide();
            }
        }
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
            var oTable = $('#events-table').bind('processing', function(e, oSettings, bShow) { showHide(bShow) }).dataTable({
                "oTableTools": {
                    "aButtons": [ "print",
                                {
                                    "sExtends": "collection",
                                    "sButtonText": "Save",
                                    "aButtons": [ "csv", "xls", "pdf" ]
                                }
                                ],
                    "sSwfPath": "{{ url_for('static', filename='copy_csv_xls_pdf.swf') }}",
                },
                responsive: true,
                pagingType: "full_numbers",
                "bSort": false,
                "bStateSave": true,
                "iCookieDuration": 60*60*24,
                "bServerSide": true,
                "bProcessing": true,
                "columns":  [
                    {"type": "date" },
                ],
                "sAjaxSource": "/log/retrieve_events_paging_data",
                "aaSorting": [[0, "desc" ]],
                "oLanguage": {
                    "sInfoFiltered": "",
                    "sInfo": "_START_ to _END_ of _TOTAL_",
                    "sInfoEmpty": "No Results",
                    "sInfoThousands": "",
                    "sEmptyTable": " ",
                    "sProcessing": "",
                },
                "aoColumns": [
                    {"mRender": RenderDateLocal },
                    null,
                    null
                ],
                "fnInitComplete": function() {
                    $('#loading').stop();
                    $('#loading').hide();
                    $('#datatable').show();
                    $('#clear').css('display', 'block');
                    this.fnAdjustColumnSizing();
                },
            });
            var tt = new $.fn.dataTable.TableTools(oTable, { "sSwfPath": "{{ url_for('static', filename='copy_csv_xls_pdf.swf')}}"});
            $(tt.fnContainer() ).insertBefore('div.dataTables_wrapper');
            $('#clearbutton').on('click', function() {
                $.confirm({
                    content: "Are you sure?",
                    title: "Clear Event Log",
                    confirm: function(button) {
                        $.ajax({
                            url: "/log/delete",
                        }).done( function( data ) {
                            oTable.fnClearTable();
                        });
                    },
                    cancel: function(button) {
                    },
                    confirmButton: "Yes",
                    cancelButton: "No",
                    post: false,
                });
            });
        });
    </script>
