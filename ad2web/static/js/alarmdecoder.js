var AlarmDecoder = function() {
    var AlarmDecoder = {};
    var _socket = null;

    AlarmDecoder.init = function() {
        this.connect("/alarmdecoder");
    };

    AlarmDecoder.connect = function(namespace) {
        _socket = io.connect(namespace, {
            'reconnect': true,
            'reconnection delay': 500,
            'max reconnection attempts': Infinity,
        });

        _socket.on('connect', function() { });
        _socket.on('disconnect', function() { });

        _socket.on('message', function(msg) {
            obj = JSON.parse(msg);

            msg = obj.message;
            msg.message_type = obj.message_type;

            PubSub.publish('message', msg);
        });

        _socket.on('event', function(msg) {
            obj = JSON.parse(msg);

            PubSub.publish('event', obj);
        });

        _socket.on('test', function(msg) {
            obj = JSON.parse(msg);

            PubSub.publish('test', obj);
        });

        _socket.on('device_open', function(msg) {
            obj = JSON.parse(msg)

            PubSub.publish('device_open', obj);
        });

        _socket.on('device_close', function(msg) {
            obj = JSON.parse(msg)

            PubSub.publish('device_close', obj);
        });
    };

    AlarmDecoder.disconnect = function() {
        _socket.disconnect();
    };

    AlarmDecoder.emit = function(type, arg) {
        _socket.emit(type, arg);
    };

    return AlarmDecoder;
};
