function ajax_get(url, callback){
    var r = new XMLHttpRequest();
    r.open("GET", url, true);
    r.onreadystatechange = function () {
        if (r.readyState == 4 || r.status == 200) {
            callback();
        }
    };
    r.send();
}

function task_fill_notification_list(data) {
    var menu = document.getElementById(notify_menu_id);
    if (menu) {
        menu.innerHTML = "";
        for (var i=0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];
            var message = "";
            if(typeof item.actor !== 'undefined'){
                message = "user '" + item.actor + "' ";
            }
            if(typeof item.verb !== 'undefined'){
                message += " " + item.verb;
            }
            if(typeof item.target !== 'undefined'){
                message += " <a href='" + item.target_url + "'>" + item.target + "</a>";
            }

            message += " <a onclick='mark_as_read(this, " + item.slug + ")' href='#'>" + "<b>X</b>" + "</a>";
            menu.innerHTML = menu.innerHTML + "<li>"+ message +"</li>";
        }

        if (data.unread_list.length){
            menu.innerHTML = menu.innerHTML + "<a onclick='mark_all_as_read()' href='#'>(all as read)</a>";
        }
    }
}

function mark_all_as_read() {
    ajax_get(notify_mark_all_unread_url, function () {
        var menu = document.getElementById(notify_menu_id);
        if (menu){
            menu.innerHTML = "";
        }
    });

    return false;
}

function mark_as_read(self, slug) {
    var mark_as_read_url = '/inbox/notifications/mark-as-read/' + slug + '/';
    ajax_get(mark_as_read_url, function () {
        var li = self.parentElement;
        var menu = li.parentElement;
        menu.removeChild(li);

        if (menu.childElementCount == 1){
            // if no notifications remove "(all as read)" element
            menu.removeChild(menu.firstChild);
        }
    });

    return false;
}

