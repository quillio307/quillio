var socket;
$(document).ready(function(){
    var url =window.location.href;
    var args =url.split('/');

    var user = args[args.length-2];
    var room = args[args.length-1];

    var mic_toggle = false;
    $("#mic").click(function () {

        $("#mic").attr('style', '');
        mic_toggle = true;
        socket.emit('silenceAll', {room: room, user: user});
        mediaStream.getAudioTracks()[0].enabled = true;
    });

    $("#start").click(function () {
        socket.emit('start', {room: room, user: user})
    });
    $("#end").click(function () {
        socket.emit('end', {room: room, user: user})
    });
    socket = io.connect('http://localhost:5000/meetings');

    socket.on('receivemsg', function(msg) {
        console.log(msg);
        msglog(msg.data);
    });

    socket.emit('join', {
        user_id: user,
        room_id: room
    });

    socket.on('silence', function () {
        console.log("Received silence command.");
        mic_toggle = !mic_toggle;
        $("#mic").attr('style', 'background:gray;');
        mediaStream.getAudioTracks()[0].enabled = false;
    });

    var mediaRecorder;
    var mediaStream;
    var handleSuccess = function(stream) {
        mediaStream = stream;
        const options = {mimeType: 'audio/webm'};
        mediaRecorder= new MediaRecorder(stream, options);
        const recordedChunks = [];
        mediaRecorder.addEventListener('dataavailable', function(e) {
          if (e.data.size > 0) {
              //if(mic_toggle){
                  recordedChunks.push(e.data);
              //}else{
                  //recordedChunks.push(e.data.size)
              //}
          }
        });

        mediaRecorder.addEventListener('stop', function() {
            saveData(new Blob(recordedChunks), "meeting_audio"+new Date()+".wav");
        });

    };
    navigator.mediaDevices.getUserMedia({ audio: true, video: false })
      .then(handleSuccess);

    socket.on('startMeeting', function () {
        msglog("Meeting Started");
        mediaRecorder.start();
    });
    socket.on('endMeeting', function () {
        msglog("Meeting Ended");
        mediaRecorder.stop();
    });

    var msglog = function(txt) {
        $('ul#msgboard').append('<li>'+ txt +'</li>');
    };
    var saveData = (function () {
        var a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        return function (data, fileName) {
            var url = window.URL.createObjectURL(data);
            a.href = url;
            a.download = fileName;
            a.click();
            window.URL.revokeObjectURL(url);
        };
    }());
});