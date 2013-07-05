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
		map.setRoutes(state.routes)
	}

	window.setState = setState;

	$(function() {
		map = Map('map', 'icio.map-wdu4ouxy');

		var activeReq;
		$('#query').livechange(function() {
			if (activeReq) activeReq.abort();
			var query = $(this).val();

			activeReq = $.get('/routes', {'query': query}, function(resp) {
				setState(resp);
				activeReq = null;
			});
		}).focus();

		// setState({routes: [
		// 	[{lon: 0, lat: 0}, {lon: 30, lat: 30, name: "TR"}],
		// 	[{lon: 0, lat: 0}, {lon: 30, lat: -30, name: "BR"}],
		// 	[{lon: 0, lat: 0}, {lon: -30, lat: 30, name: "TL"}],
		// 	[{lon: 0, lat: 0}, {lon: -30, lat: -30, name: "BL"}],

		// 	[{lon: 80+30, lat: 30, name: "TR"}, {lon: 80+0, lat: 0}],
		// 	[{lon: 80+30, lat: -30, name: "BR"}, {lon: 80+0, lat: 0}],
		// 	[{lon: 80+-30, lat: 30, name: "TL"}, {lon: 80+0, lat: 0}],
		// 	[{lon: 80+-30, lat: -30, name: "BL"}, {lon: 80+0, lat: 0}],
		// ]});

		/* setState({routes:[
			[ {lon:94.09765, lat:27.295494, name:"A1"}, {lon:0.055278, lat:51.505278, name:"B1"} ],

			// This route is problematic because it wants to wrap in the opposite direction around the world
			[ {lon:-74.0071, lat:40.7545, name:"A2"}, {lon:144.901944, lat:-37.728056, name:"B2"} ],
		]}); */
	});
});
