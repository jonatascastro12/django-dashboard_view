function Dashboard(){
}

Dashboard.show_message = function(message, type){
    type = type || 'success';
    $('#page-wrapper .col-lg-12').first().prepend('&nbsp;<div class="alert alert-'+type+' alert-dismissible">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
         message +'</div>');
}


$(document).ready(function(){
    Dashboard();
})


$(function() {
    $('#side-menu').metisMenu();
});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function() {
    $(window).bind("load resize", function() {
        topOffset = 50;
        width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        height = ((this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height) - 1;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });

    var url = window.location;
    var element = $('ul.nav a').filter(function() {
        var patt = new RegExp("^"+this.href+"(/)?([0-9]*)(/|/add|/edit/|/novo|/nova|/editar)?$");
        return patt.exec(url);
    }).addClass('active').parent().parent().addClass('in').parent().parent().addClass('in');
    if (element.is('li')) {
        element.addClass('active');
    }
});