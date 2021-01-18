$(document).ready(() => {
    $('#form_send_msg').on('submit', (e) => {
        e.preventDefault();
    });

    const socket = io.connect('http://127.0.0.1:5000');
    const username = $('#username').text();

    $('#send_msg').on('click', () => {
        socket.send({
                'msg': $('#message_input').val(),
                'username': username,
            });
        $('#message_input').val('');
    });

    socket.on('message', data => {
        if (data.msg.length > 0) {

            $('#messages').append(`<li><strong>${data.username}:</strong> ${data.msg}</li>`);
            console.log('Received message');
        }
    });
});

