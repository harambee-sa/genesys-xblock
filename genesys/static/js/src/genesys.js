/* Javascript for GenesysXBlock. */
function GenesysXBlock(runtime, element) {

	var handlerUrl = runtime.handlerUrl(element, 'test_started_handler');
    // var isOnDiv = false;
    // $('.genesys_xblock').mouseenter(function(){isOnDiv=true;});
    // $('.genesys_xblock').mouseleave(function(){isOnDiv=false;});

    $(window).unload(function() {
         return "Bye now!";
    });

    $('.genesys-test-link', element).click(function(eventObject) {
      localStorage.setItem("started_genesys", true);
      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({'started': true}),
          success: function(){
          	console.log('The test was started...')
            // Just reload the page, the correct html with the badge will be displayed
            var onlyUrl = location.href.replace(location.search,'');
            window.location = onlyUrl;
            return false;
          }
      });
    });

}
