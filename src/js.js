function onClean(idx) {
    cmd = "clean:" + idx;
    pycmd(cmd);
}


function setCleanFields() {
    $fnames = $(".fname");
    for (var i=0; i<$fnames.length; i++) {
        var $td_name = $(`#name${i}`);
        var div = `, <a onclick='onClean(${i})'>clean</a>`;
        $td_name.append(div);
    }
}
