(function(){
    'use strict';

    const screen_width = 1920;
    const screen_height = 1080;

    var cursor_moved = false;
    var cursor_x = 0;
    var cursor_y = 0;

    let sock = new WebSocket("ws://localhost:80/ws");

    sock.onopen = function(e){
        sock.send("get");
        document.title = "LoControl • Connecté!"
    };

    sock.onmessage = function(e){
        document.getElementById("screen").src = e.data;
        if(cursor_moved){
             sock.send("cursor:"+cursor_x+":"+cursor_y);
             cursor_moved = false;
        }
        setTimeout(function(){
            sock.send("get");
        }, 20);
    };

    const error = function(e){
        document.title = "LoControl • Déconnecté!";
        alert("Websocket: Connection perdu! Appuyez sur F5");
    }

    sock.onclose = error;
    sock.onerror = error;

    onmousemove = function(e){
        cursor_x = (((e.clientX - (document.documentElement.clientWidth - (document.getElementById("screen").offsetWidth))/2) * screen_width)/ 
                    document.getElementById("screen").offsetWidth).toFixed();

        cursor_y = (((e.clientY - (document.documentElement.clientHeight - (document.getElementById("screen").offsetHeight))/2) * screen_height)/
                    document.getElementById("screen").offsetHeight).toFixed();
        cursor_moved = true;
    };

    onmousedown = function(e){
        if(e["target"] == document.getElementById("screen")){
            if(window.event.which==1){
                sock.send("leftdown");
            }
            else if(window.event.which==3){
                sock.send("rightdown");
            }
        };
    }

    onmouseup = function(e){
        if(e["target"] == document.getElementById("screen")){
            if(window.event.which==1){
                sock.send("leftup");
            }
            else if(window.event.which==3){
                sock.send("rightup");
            }
        };
    };

}());