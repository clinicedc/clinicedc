function edcLabelReady() {

	// var labelTemplates = JSON.parse( label_templates );

	var post = $.ajax({
		url: Urls['edc_label:home_url'](),
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

function changeSessionPrinter( data ) {}

function updatePage( data ) {
	var print_server = JSON.parse( data.print_server );
	var printers = JSON.parse( data.printers );
	var label_templates = JSON.parse( data.label_templates );

	$( "#div-printers-panel" ).text( 'Printers@' + data.default_cups_server_ip );

	updateLabelTemplates( label_templates );
	updatePrinters( printers, data.default_printer_name );

	$( "#alert-print-server-wait" ).hide();
	$( "#alert-print-error" ).hide();
	$( "#alert-print-server-error" ).hide();
	if( data.print_server_error != '' &  data.print_server_error != null ) {
		$( "#alert-print-server-error" ).text( data.print_server_error ).append( '<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' );
		$( "#alert-print-server-error" ).show();
	} else {
		$( "#alert-print-server-error" ).hide();
	};
}


function updatePrinters( printers, default_printer_name ){
	$.each( printers, function( printer_name, printer ) {
		if( printer_name == default_printer_name ) {
			row = '<tr id="row-printer-printer_name" class="success"><td colspan="5">Label: ' + printer_name +'<span class="pull-right">default</span></td></tr>';
		} else {
			row = '<tr id="row-printer-printer_name"><td colspan="5">Label: ' + printer_name +'</td></tr>';
		};
		$( "#tbl-printers" ).append(row);
		row = '<tr><td>' + printer.printer_info + '</td>' +
			  '<td>' + printer.printer_make_and_model + '</td>' +
			  '<td>' + printer.printer_location + '</td>' +
			  '<td>' + printer.printer_is_shared + '</td>' +
			  '<td>' + printer.printer_state + '</td></tr>';
		$( "#tbl-printers" ).append(row);
	});
}

function updateLabelTemplates( label_templates ) {
	$.each( label_templates, function( label_name, label_template ) {
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
			$( "#alert-print-success" ).hide();
			$( "#alert-print-error" ).hide();
			testLabel(label_template);
		});
	});
}

function testLabel(label_template){
	var post = $.ajax({
		url: Urls['edc_label:print-test-label'](label_template.label),
		type: 'GET',
		dataType: 'json',
		contentType: 'application/json',
		processData: false,
	});

	post.done(function ( data ) {
		if ( data != null ) {
			if( data.label_message != null ) {
				$( "#alert-print-success" ).text(data.label_message).append('<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>');
				$( "#alert-print-success" ).show();
			};
			if( data.label_error_message != null ) {
				$( "#alert-print-error" ).text(data.label_error_message).append('<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>');
				$( "#alert-print-error" ).show();
			};
		};
	});

	post.fail( function( jqXHR, textStatus, errorThrown ) {});
}
