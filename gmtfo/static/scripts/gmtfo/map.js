define(["mapbox"], function(mapbox) {
	mapbox = L.mapbox; // FIXME Requirejs isn't being setup correctly
	return function(e, mapId)
	{
		var map = mapbox.map(e, mapId, {
			'legendControl': false
		});
		map.zoomControl.removeFrom(map);
		// map.dragging.disable();
		// map.touchZoom.disable();
		// map.doubleClickZoom.disable();
		// map.scrollWheelZoom.disable();

		var routesLayer = mapbox.markerLayer();
		routesLayer.addTo(map);
		routesLayer.setGeoJSON({
		    type: "FeatureCollection",
		    features: [{
		        type: "Feature",
		        geometry: {
		            type: "Point",
		            coordinates: [102.0, 0.5]
		        },
		        properties: { }
		    }]
		});

		function setRoutes(routes) {
			// Handle empty responses
			if (!routes || !routes.length) {
				return;
			}

			var feature = {
				"type": "FeatureCollection",
				"features": []
			};
			for (var r = 0, R = routes.length; r < R; r++) {
				for (var p = 0, P = routes[r].length; p < P; p++) {
					var point = routes[r][p];
					point.title = point.name
					feature.features.push({
						"type": "Feature",
						"geometry": {
							"type": "Point",
							"coordinates": [point.lon, point.lat]
						},
						"properties": point
					});
				}
			}

			console.log(feature);
			routesLayer.setGeoJSON(feature);
		}

		return {
			'map': map,
			'setRoutes': setRoutes
		};
	};
});
