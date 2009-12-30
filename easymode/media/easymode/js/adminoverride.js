
function dismissAddAnotherPopup(win, newId, newRepr) {

	var name = windowname_to_id(win.name);
	var from = document.getElementById(name);
	var toId = name + "_to";
	var to = document.getElementById(toId);

	if (! (from || to) && win) {

		win.close();
		window.location.reload( false );
				
	} else {
		// the old function
		newId = html_unescape(newId);
	    newRepr = html_unescape(newRepr);
	    if (from) {
	        if (from.nodeName == 'SELECT') {
	            var o = new Option(newRepr, newId);
	            from.options[from.options.length] = o;
	            o.selected = true;
	        } else if (from.nodeName == 'INPUT') {
	            if (from.className.indexOf('vManyToManyRawIdAdminField') != -1 && from.value) {
	                from.value += ',' + newId;
	            } else {
	                from.value = newId;
	            }
	        }
	    } else {
	        var toId = name + "_to";
	        to = document.getElementById(toId);
	        var o = new Option(newRepr, newId);
	        SelectBox.add_to_cache(toId, o);
	        SelectBox.redisplay(toId);
	    }
	    win.close();		
	}
}
