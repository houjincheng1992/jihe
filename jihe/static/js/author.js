$(function () {
    $("ul").mouseover(function(e){
        var e = e || window.event;//处理兼容性
        var target = e.target || e.srcElement;
        if (target.nodeName.toLowerCase() === "img") {
            $(target.parentNode.parentNode.lastElementChild).addClass("addOpacity")
        }
    })
    $("ul").mouseout(function(e){
        var e = e || window.event;//处理兼容性
        var target = e.target || e.srcElement;
        if (target.nodeName.toLowerCase() === "img") {
            $(target.parentNode.parentNode.lastElementChild).removeClass("addOpacity")
        }
    })
});
