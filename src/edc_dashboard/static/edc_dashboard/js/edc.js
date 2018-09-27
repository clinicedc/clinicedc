
function copyStringToClipboard(value) {
    var el = document.createElement('textarea');
    el.value = value;
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    document.body.removeChild(el);
}
