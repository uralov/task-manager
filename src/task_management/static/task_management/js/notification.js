function task_fill_notification_list(data) {
    var menu = document.getElementById(notify_menu_id);
    if (menu) {
        menu.innerHTML = "";
        for (var i=0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];
            var message = ""
            if(typeof item.actor !== 'undefined'){
                message = item.actor;
            }
            if(typeof item.verb !== 'undefined'){
                message = message + " " + item.verb;
            }
            if(typeof item.target !== 'undefined'){
                message = message + " <a href='" + item.target_url + "'>" + item.target + "</a>";
            }

            menu.innerHTML = menu.innerHTML + "<li>"+ message +"</li>";
        }

        if (data.unread_list.length){
            menu.innerHTML = menu.innerHTML + "<a onclick='mark_read()' href='#'>(mark all as read)</a>";
        }
    }
}

function mark_read() {
    alert('qwe');
    var r = new XMLHttpRequest();
        r.open("GET", notify_mark_all_unread_url, true);
        r.onreadystatechange = function () {
            if (r.readyState == 4 || r.status == 200) {
                var menu = document.getElementById(notify_menu_id);
                if (menu){
                    menu.innerHTML = "";
                }
            }
        }
        r.send();
    return false;
}