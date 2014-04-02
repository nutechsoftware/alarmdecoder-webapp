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

        _socket.on('connect', function() {
            console.log('websocket opened');
        });

        _socket.on('message', function(msg) {
            obj = JSON.parse(msg);

            msg = obj.message;
            msg.message_type = obj.message_type;

            PubSub.publish('message', msg);
        });

        _socket.on('event', function(msg) {
            obj = JSON.parse(msg);

            console.log('obj', obj);

            PubSub.publish('event', obj);
        });

        _socket.on('disconnect', function() {
            console.log('websocket closed');
        });

        _socket.on('test', function(msg) {
            obj = JSON.parse(msg);

            console.log('test', obj);

            PubSub.publish('test', obj);
        });

        _socket.on('device_open', function(msg) {
            obj = JSON.parse(msg)

            console.log('device opened.');
            PubSub.publish('device_open', obj);
        });

        _socket.on('device_close', function(msg) {
            obj = JSON.parse(msg)

            console.log('device closed.');
            PubSub.publish('device_close', obj);
        });
    };

    AlarmDecoder.emit = function(type, arg) {
        _socket.emit(type, arg);
    };

    return AlarmDecoder;
};
