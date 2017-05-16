<script type="text/javascript">
    $(document).ready(function() {
        var upload_label = $('div#upload-label');
        var upload_progressbar = $('div#upload-status');

        PubSub.subscribe('firmwareupload', function(type, msg) {
            var stage = msg.stage;

            if (stage == "STAGE_START") {
                upload_label.text("Starting upload..");
            }
            else if (stage == "STAGE_WAITING") {
                upload_label.text("Waiting for device..");
            }
            else if (stage == "STAGE_BOOT") {
                upload_label.text("Rebooting device..");
            }
            else if (stage == "STAGE_LOAD") {
                upload_label.text("Waiting for boot loader..");
            }
            else if (stage == "STAGE_UPLOADING") {
                upload_label.text("Uploading firmware: " + msg.percent + "%");
                upload_progressbar.progressbar({ value: msg.percent });
            }
            else if (stage == "STAGE_DONE") {
                upload_label.text("Firmware upload complete!");
                $('div#upload-retry').hide();
                upload_progressbar.progressbar({ value: 100 });
            }
            else if (stage == "STAGE_CONFIGURE") {
                upload_label.text("Reconfiguring device..");
            }
            else if (stage == "STAGE_FINISHED") {
                upload_label.text("Complete!");
            }
            else if (stage == "STAGE_ERROR") {
                console.log(msg.error);
                upload_label.text(msg.error);
                upload_label.addClass('upload-error');
                upload_progressbar.progressbar({ value: -1 });
                $('div#upload-retry').show();
            }
        });

        $('button#upload-retry-button').click(function() {
            upload_label.removeClass('upload-error');
            upload_progressbar.progressbar({ value: false });
            $('div#upload-retry').hide();

            decoder.emit('firmwareupload');
        });

        $('div#upload-status').progressbar({ value: false });
        decoder.emit('firmwareupload');
    });
</script>
