jQuery(function($) {
    $('div[id$=changelist] table tbody').sortable({

        handle: 'th',
		update: function() {
			$(this).find('tr').each(function(i) {
				$(this).find('input[class$=vIntegerField]').val(i+1);
			});
		}
    });

    $('div[id$=changelist] table tbody tr th').css('cursor', 'move');
	$('div[id$=changelist] table thead tr th[class$=sorted ascending]').hide();
    $('div[id$=changelist] table tbody tr').find('input[class$=vIntegerField]').parent().hide();
});


