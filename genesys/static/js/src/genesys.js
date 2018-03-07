/* Javascript for GenesysXBlock. */
function GenesysXBlock(runtime, element) {

  	        $('.recap-download-btn').click(function(event){
            event.preventDefault();
            event.stopImmediatePropagation()
            
            noteFormUrl = $('.recap-instructor-form').attr('action');
            var my_data = { 'user_id': pdf_element_id, 'these_blocks': selected_id}
            SpinnerCallback(true, function() {
                $.ajax({
                    url: noteFormUrl,
                    method: 'POST',
                    data: JSON.stringify(my_data),
                    success: function(data) {
                        pdf_element = data['html'];
                    }
                });
            });
        });



}
