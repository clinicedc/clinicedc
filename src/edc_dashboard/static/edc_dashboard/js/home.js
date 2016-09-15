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

	getSubjectSearchForm();

	$( '#pnl-most-recent-subjects' ).hide();
	$( '#btn-hide-most-recent-subjects' ).hide();

	$( '#btn-toggle-search' ).text( 'Close' );
	$( '#btn-toggle-search' ).click( function() {
		// toggle search and other buttons in panel header
		$( this ).text( function( i, text ){
	          text = ( text === 'Search' ) ? 'Close' : 'Search';
	          if ( text == 'Search' ) {
	        	  $( '#btn-hide-most-recent-subjects' ).hide();
	        	  $( '#btn-show-most-recent-subjects' ).hide();
	          } else {
	        	  $( '#btn-hide-most-recent-subjects' ).hide();
	        	  $( '#btn-show-most-recent-subjects' ).show();
	          };
	          return text;
	      });
	});

	$( '#btn-hide-most-recent-subjects' ).click( function( e ) {
		e.preventDefault();
		$( '#btn-hide-most-recent-subjects' ).hide();
		$( '#btn-show-most-recent-subjects' ).show();
		$( '#pnl-most-recent-subjects' ).hide();
	});

	$( '#btn-show-most-recent-subjects' ).click( function( e ) {
		e.preventDefault();
		getSubjects( 1 );
	});

}


function getSubjectSearchForm() {
	//Gets the subject search form from the view rendered as html and inserts into the DOM.
	var post = $.ajax({
		url: Urls['edc-dashboard:subject-search'](),
		type: 'POST',
	});

	post.done(function ( data ) {
		insertSearchForm( data.form_html );
	});

	post.fail( function( jqXHR, textStatus, errorThrown ) {
		alert( errorThrown );
	});	
}

function insertSearchForm( form_html ) {
	//Inserts the form_html into the DOM
	$( '#subject-search' ).html( form_html );

	$( '#form-subject-search' ).on( 'submit', function(e) {
		e.preventDefault();
		searchSubjects( $( '#form-subject-search' ).serialize() );
	});	
}


function searchSubjects( form_data ) {

	//Passes search form data to the view and inserts validated form back into the DOM.
	var ajPost = $.ajax({
		url: Urls['edc-dashboard:subject-search'](),
		type: 'POST',
		data: form_data,
	});

	ajPost.done(function ( data ) {
		var form_html = data.form_html;
        var object_list = JSON.parse( data.object_list );
        var paginator = JSON.parse( data.paginator );

		// re-insert the updated search form
		insertSearchForm( form_html );

		// update the Subjects table
		updateSubjectsTable( object_list, paginator );

	});

	ajPost.fail( function( jqXHR, textStatus, errorThrown ) {
		console.log( errorThrown );
	});
	
}


function gotoSubject( subject_identifier ) {
	// Submits the search form with the given subject_identifier.

	$( '#id_search_term' ).val( subject_identifier );
	$( '#form-subject-search' ).submit();
	$( '#btn-toggle-search' ).click();

	$( '#spn-current-subject' ).text( 'Subject: '+ subject_identifier );
	$( '#pnl-current-subject' ).show();

	return false;
}


function getSubjects( page_number ) {

	// Gets a paginated queryset of "subjects" and adds each row to the table.
	var ajMostRecent = $.ajax({
		url: Urls['edc-dashboard:most-recent']('subjects', page_number),
		type: 'GET',
	});

	ajMostRecent.done(function ( data ) {
		// build rows with returned data and show the table
		var object_list = JSON.parse( data.object_list );
		var paginator = JSON.parse( data.paginator );

		updateSubjectsTable( object_list, paginator );

	});

	ajMostRecent.fail( function( jqXHR, textStatus, errorThrown ) {
		alert( 'error' );
		console.log( errorThrown );
		$( '#btn-hide-most-recent-subjects' ).hide();
		$( '#btn-show-most-recent-subjects' ).show();
	});
	
}


function updateSubjectsTable( object_list, paginator ) {
	//Updates the subjects table.
	var rows = '';
	$.each( object_list, function( key, obj ) {
		rows += '<tr>' +
		'<td><button id="btn-' + obj.fields.subject_identifier + '" class="btn btn-sm btn-default">Go</button></td>' +
		'<td>' + obj.fields.subject_identifier + '</td>' +
		'<td>' + obj.fields.first_name + ' (' + obj.fields.initials + ')</td>' +
		'<td>' + obj.fields.gender + '</td>' +
		'<td>' + obj.fields.dob + '</td>' +
		'<td>' + obj.fields.user_created  + '</td>' +
		'<td>' + obj.fields.created + '</td>' +
		'</tr>';
	});

	// add rows to table
	$( '#table-most-recent-subjects tbody' ).html( rows );

	// add click event for go button
	$.each( object_list, function( key, obj ) {
		$( '#btn-' + obj.fields.subject_identifier ).click( function( e ){
			e.preventDefault();
			gotoSubject( obj.fields.subject_identifier );
		});
	});

	// show table and switch buttons
	$( '#pnl-most-recent-subjects' ).show();
	$( '#btn-hide-most-recent-subjects' ).show();
	$( '#btn-show-most-recent-subjects' ).hide();

	updatePager( paginator );

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


function updatePager( paginator ) {
	$( '#spn-pager-pages' ).text( 'Page ' + paginator.number + '/' + paginator.num_pages );
	if (paginator.num_pages === 1 ) {
		$( '#btn-pager-next').prop( 'disabled', true); 
		$( '#btn-pager-last').prop( 'disabled', true );
		$( '#btn-pager-first').prop( 'disabled', true); 
		$( '#btn-pager-previous').prop( 'disabled', true ); 
	} else {
		if (paginator.num_pages === paginator.number) {
			$( '#btn-pager-next').prop( 'disabled', true); 
			$( '#btn-pager-last').prop( 'disabled', true ); 
		} else {
			$( '#btn-pager-next').prop( 'disabled', false ); 
			$( '#btn-pager-last').prop( 'disabled', false );
			$( '#btn-pager-next').click( function ( e ) {
				e.preventDefault();
				getSubjects( paginator.number + 1 );
			});
			$( '#btn-pager-last').click( function ( e ) {
				e.preventDefault();
				getSubjects( paginator.count );
			});
		};
		if (paginator.number === 1 ) {
			$( '#btn-pager-first').prop( 'disabled', true); 
			$( '#btn-pager-previous').prop( 'disabled', true ); 
		} else {
			$( '#btn-pager-first').prop( 'disabled', false ); 
			$( '#btn-pager-previous').prop( 'disabled', false ); 
			$( '#btn-pager-previous').click( function ( e ) {
				e.preventDefault();
				getSubjects( paginator.number - 1 );
			});
			$( '#btn-pager-first').click( function ( e ) {
				e.preventDefault();
				getSubjects( 1 );
			});
		};
	};
}

