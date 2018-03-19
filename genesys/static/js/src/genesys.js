/* Javascript for GenesysXBlock. */
function GenesysXBlock(runtime, element) {

	var handlerUrl = runtime.handlerUrl(element, 'test_started_handler');
    var completedUrl = runtime.handlerUrl(element, 'test_completed_handler');

    function backToPage() {
    // The user returned to the page, check if results are available
    // Do something
        if (localStorage.getItem("test_result_received") == null) {
            $.ajax({
                type: "POST",
                url: completedUrl,
                data: JSON.stringify({'started': true}),
                success: function(data){
                    console.log(data)
                    if (data['completed'] == true){
                        localStorage.setItem("test_result_received", true)
                        var onlyUrl = location.href.replace(location.search,'');
                        window.location = onlyUrl;
                        return false;
                    }
                }
            });
        }
    }

    window.onfocus = backToPage;


    $('.genesys-test-link', element).click(function(eventObject) {
      localStorage.setItem("started_genesys", true);
      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({'started': true}),
          success: function(data){
          	console.log('The test was started...')
            // Just reload the page, the correct html with the badge will be displayed
            var onlyUrl = location.href.replace(location.search,'');
            window.location = onlyUrl;
            return false;
          }
      });
    });

}
