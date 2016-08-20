function edcLabelReady( label_templates, print_server_error ) {
	var labelTemplates = JSON.parse( label_templates );

	$("#alert-print-server-wait").hide();
	if( print_server_error != null ) {
		$("#alert-print-server-error").text( print_server_error ).append( '<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' );
		$("#alert-print-server-error").show();
	} else {
		$("#alert-print-server-error").hide();
	};

	$.each( labelTemplates, function( label_name, label_template ) {
		test_context = JSON.stringify(label_template.test_context);
		row = '<tr>' +
			  '<td>' + label_template.verbose_name + '</td>' +
              '<td>'+ label_template.label + '</td>' +
              '<td>' + label_template.file + '<br><span id="span-label-template-test-context-' + label_template.label +'" title="" class="text-success" style="display:none"><small>test data</small></span></td>' +
              '<td><a id="btn-test-' + label_template.label +'" class="btn btn-default" href="">Test</a></td>' +
              '</tr>';
		$("#tbl-label-templates").append(row);
		if ( test_context != '{}') {
			$( '#span-label-template-test-context-' + label_template.label ).show();
			$( '#span-label-template-test-context-' + label_template.label ).attr('title', test_context);

		};
		$("#btn-test-" + label_template.label).click( function (e) {
			e.preventDefault();
			$("#alert-print-success").hide();
			$("#alert-print-error").hide();
			testLabel(label_template);
		});
	});
}

function testLabel(label_template){
	var post = $.ajax({
		url: Urls['edc-label:print-test-label'](label_template.label),
		type: 'GET',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
	});

	post.done(function ( data ) {
		if ( data != null ) {
			if( data.label_message != null ) {
				$("#alert-print-success").text(data.label_message).append('<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>');
				$("#alert-print-success").show();
			};
			if( data.label_error_message != null ) {
				$("#alert-print-error").text(data.label_error_message).append('<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>');
				$("#alert-print-error").show();
			};
		};
	});

	post.fail( function( jqXHR, textStatus, errorThrown ) {
		alert(errorThrown);
	});
}
