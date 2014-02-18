var AlarmDecoder = function() {
    var AlarmDecoder = {};
    var _socket = null;

    AlarmDecoder.init = function() {
        this.connect("/alarmdecoder");
    };

    AlarmDecoder.connect = function(namespace) {
        _socket = io.connect(namespace);

        _socket.on('connect', function() {
            console.log('websocket opened');
        });

        _socket.on('message', function(msg) {
            obj = JSON.parse(msg);

            PubSub.publish('message', obj);
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
    };

    AlarmDecoder.emit = function(type, arg) {
        _socket.emit(type, arg);
    };

    return AlarmDecoder;
};
