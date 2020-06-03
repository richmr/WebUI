// Make a POST JSON call with jQuery and append result to opscheck-text div
dataToSend = {"returnthis":"If you see this message twice, jQuery & dynamic pages are working<br>"};

$.post( "opscheck.html", JSON.stringify(dataToSend), function( data ) {
  $( "#opscheck-text" ).append( data );
});
