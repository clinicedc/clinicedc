function edcDashboardReady() {
	var csrftoken = Cookies.get('csrftoken');

	// configure AJAX header with csrf tokens
	$.ajaxSetup({
	beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
			};
		}
	});	

	$( '#form-subject-search' ).on( 'submit', function(e) {
		e.preventDefault();
		search_subject_consent( $( '#form-subject-search' ).serialize() );
	});
	$( '#button-id-show-most-recent-subjects' ).click( function() {
		getMostRecentSubjects();
		$( '#button-id-hide-most-recent-subjects' ).show();
		$( '#button-id-show-most-recent-subjects' ).hide();
	});
	$( '#panel-most-recent-subjects-table' ).hide();
	$( '#button-id-hide-most-recent-subjects' ).hide();
	$( '#button-id-hide-most-recent-subjects' ).click( function() {
		$( '#button-id-hide-most-recent-subjects' ).hide();
		$( '#button-id-show-most-recent-subjects' ).show();
		$( '#panel-most-recent-subjects-table' ).hide();
	});
}

function search_subject_consent( form_data ) {
	var post = $.ajax({
		url: Urls['home_url'](),
		type: 'POST',
		data: form_data,
	});

	post.done(function ( data ) {
		var subject_consent = JSON.parse( data.subject_consent );
		$( '#panel-consent' ).removeClass( 'panel-default' );
		$( '#panel-consent' ).addClass( 'panel-success' );
		$( '#panel-consent-heading' ).attr( 'href', '#collapse-consent' );
		$( '#panel-consent-table' ).html( getRows( subject_consent ) );
	});

	post.fail( function( jqXHR, textStatus, errorThrown ) {});
	
}

function getMostRecentSubjects() {
	var url = Urls['edc-dashboard:most-recent']('subjects');
	var post = $.ajax({
		url: url,
		type: 'GET',
	});

	post.done(function ( data ) {
		// var data = JSON.parse( data );
		rows = ''
		$.each( data, function( key, obj ) {
			rows += '<tr><td>' + obj.fields.subject_identifier + '</td><td>' + obj.fields.first_name + ' (' + obj.fields.initials + ')</td><td>' + obj.fields.gender + '</td><td>' + obj.fields.dob + '</td><td>' + obj.fields.user_created + '</td><td>' + obj.fields.created + '</td></tr>';
		});
		$( '#panel-most-recent-subjects-table' ).show();
		$( '#table-most-recent-subjects thead' ).html( '<th>identifier</th><th>name</th><th>gender</th><th>dob</th><th>created</th>' );
		$( '#table-most-recent-subjects tbody' ).html( rows );

	});

	post.fail( function( jqXHR, textStatus, errorThrown ) {
		alert(errorThrown);
	});
	
}

function getRow( fields ) {
	var row = '';
	var col = '';
	$.each( fields, function( attr, value ) {
		col += '<td>' + value + '</td>';
	});
	row += '<tr>' + col + '</tr>';
	return row; 
}