function onClean(idx) {
  cmd = "clean:" + idx;
  pycmd(cmd);
}

function setCleanFields() {
  $fnames = $(".fname");
  for (var i = 0; i < $fnames.length; i++) {
    var $td_name = $(`#name${i}`);
    var div = `, <a onclick='onClean(${i})'>clean</a>`;
    $td_name.append(div);
  }
}

function makeNonContentEditable() {
  console.log("in makeNonContentEditable");
  var allfields = document.getElementsByClassName("field clearfix");
  for (var i = 0; i < allfields.length; i++) {
    $(allfields.item(i)).prop("contenteditable", false);
  }
}
