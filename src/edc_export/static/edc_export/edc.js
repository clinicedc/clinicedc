$(window).bind("load", function () {
    $("#work-in-progress").hide();
    return true;
});

function selectAll(app_config_name,label){
    $(":input[id^=chk_" + app_config_name + "_" + label + "]").prop('checked', $("#select_all_" + app_config_name + "_" + label).prop("checked"));
    return true;
};

function toggle(id){
    $("input[id=" + id +"]").prop('checked', !$("input[id=" + id +"]").prop("checked"));
    return true;
}

function confirm(){
    $("#btn-confirm").prop("disabled",true);
    $("#work-in-progress").show();
    return true;
}