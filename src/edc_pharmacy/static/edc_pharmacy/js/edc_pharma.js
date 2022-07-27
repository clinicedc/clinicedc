function edcPharmaReady() {

	var post = $.ajax({
		url: Urls['edc-label:home_url'](),
		type: 'GET',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
	});

	post.done(function ( data ) {
		updatePage( data );
	});

	post.fail( function( jqXHR, textStatus, errorThrown ) {});
}

function updatePage( data ) {
	var label_templates = JSON.parse( data.label_templates );
	updateDispenseData( label_templates );
}

function updateDispenseData( label_templates ) {
	 $.each( label_templates, function( label_name, label_template ) {
		test_context = JSON.stringify(label_template.test_context);
		dispense_data = JSON.parse(JSON.stringify(label_template.test_context));
		row = '<tr>' +
			  '<td>' + dispense_data.patient + '</td>' +
              '<td>'+ dispense_data.treatment + '</td>' +
              '<td>' + dispense_data.dose + '</td>' +
              '<td>' + dispense_data.frequency_per_day + '</td>' +
              '<td><a id="btn-print-' + dispense_data.doctor +'" class="btn btn-default" href="">Print</a></td>' +
              '</tr>';
		$("#tbl-dispense-data").append(row);
		if ( test_context != '{}') {
			$( '#span-label-template-test-context-' + label_template.label ).show();
			$( '#span-label-template-test-context-' + label_template.label ).attr('title', test_context);

		};
	});
}