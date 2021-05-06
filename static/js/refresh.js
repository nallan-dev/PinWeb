
var refresh = function() {
    $.ajax({
      type: 'GET',
      url: '/ajax_html',
      data: ''
    }).done(function(data) {
      $('.container').html(data);
    }).fail(function() {
      console.log('ajax_fail');
    });
}

setInterval(function(){
    refresh() // this will run after every 3 seconds
}, 3000);