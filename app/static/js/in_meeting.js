let socket;
let speechsocket;
var user;
$(document).ready(function(){
    $.ajax({
      url: '/auth/getUser',
      success: function(data){
          user = JSON.parse(data);
          init();
      }
    });
});

function convertFloat32ToInt16(buffer) {
  l = buffer.length;
  buf = new Int16Array(l);
  while (l--) {
    buf[l] = Math.min(1, buffer[l])*0x7FFF;
  }
  return buf.buffer;
}

function init() {
    var context = new AudioContext();
//     // Create WebSocket connection.
    const speechsocket = new WebSocket(`ws://quillio-ws-st.herokuapp.com/?sampRate=${context.sampleRate}`);

    speechsocket.addEventListener('message', function (event) {
        let msg = JSON.parse(event.data);
        if(msg[0] && msg[0].alternatives[0]){
            let alt = msg[0].alternatives[0];
            console.log(msg[0].isFinal);
            if(msg[0].isFinal === true){
                $('#tempChunk').html('');
                $('ul#msgboard').append('<li>' + user.name + ': ' + alt.transcript +'</li>');
            }else{
                console.log(alt.transcript);
                $('#tempChunk').html(alt.transcript);
            }
        }
    });

    var url =window.location.href;
    var args =url.split('/');

    var room = args[args.length-1];
    console.log("Room joined: " +room);
    var mic_toggle = false;
    $("#mic").click(function () {

        $("#mic").attr('style', '');
        mic_toggle = true;
        socket.emit('silenceAll', {room: room, user: user.name});
        mediaStream.getAudioTracks()[0].enabled = true;
    });

    $("#start").click(function () {
        socket.emit('start', {room: room, user: user.name})
    });
    $("#end").click(function () {
        socket.emit('end', {room: room, user: user.name})
    });
    socket = io.connect('http://localhost:5000/meeting');

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

    var handleSuccess = function(stream) {

        var source = context.createMediaStreamSource(stream);
        var processor = context.createScriptProcessor(1024, 1, 1);

        source.connect(processor);
        processor.connect(context.destination);
        console.log(context.sampleRate);
        processor.onaudioprocess = function(e) {
          // Do something with the data, i.e Convert this to WAV
          if(speechsocket.readyState == 1){
            speechsocket.send(convertFloat32ToInt16(e.inputBuffer.getChannelData(0)));
          }

        };
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
}