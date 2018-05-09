$(function () {
    console.log('进来了')
    // $(".authors").hover(function(){
    //     console.log('slfjs')
    //     $(".authorInfo").css("opacity","1");
    // }).mouseout(function(){
    //     $(".authorInfo").css("opacity", "0");
    // })

    // $(".authors").on("hover", "li", function(event) {
    //     // var target = $(event.target);
    //     console.log('脸上肌肤来说')
    // })

    $(".authors").hover(function(e){
        var e = e || window.event;//处理兼容性
        var target = e.target || e.srcElement;
        console.log(target, target.nodeName, 'lsjdlf ') 
    })
});
