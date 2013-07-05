//
//                               __  ____    
//              ____ _____ ___  / /_/ __/___ 
//             / __ `/ __ `__ \/ __/ /_/ __ \
//            / /_/ / / / / / / /_/ __/ /_/ /
//            \__, /_/ /_/ /_/\__/_/  \____/ 
//           /____/                          
//

define(["jquery", "./map"], function($, Map)
{
	$.fn.livechange = function(callback) {
		this.each(function() {
			var elem = $(this);
			elem.data('oldVal', elem.val());
			elem.bind("propertychange keyup input paste", function(event){
				if (elem.data('oldVal') != elem.val()) {
					elem.data('oldVal', elem.val());
					callback.call(this);
				}
			});
		});
		return this;
	};

	var map;
	var markerLayer;

	function setState(state) {
		console.log(state);
		map.setRoutes(state.routes)
	}

	$(function() {
		map = Map('map', 'icio.map-wdu4ouxy');

		var activeReq;
		$('#query').livechange(function() {
			if (activeReq) activeReq.abort();
			var query = $(this).val();
			if (!query) return;

			activeReq = $.get('/routes', {'query': query}, function(resp) {
				setState(resp);
				activeReq = null;
			});
		}).focus();
	});
});
