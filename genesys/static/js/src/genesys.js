/* Javascript for GenesysXBlock. */
function GenesysXBlock(runtime, element) {

	var handlerUrl = runtime.handlerUrl(element, 'test_started_handler');


  $('.genesys-test-link', element).click(function(eventObject) {
    localStorage.setItem("started_genesys", true);
    $.ajax({
        type: "POST",
        url: handlerUrl,
        data: JSON.stringify({'started': true}),
        success: function(){
        	console.log('The test was started.')
        }
    });
  });

}
