define(["mapbox", "leaflet-d3"], function(mapbox, d3Layer)
{
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

		var pathsLayer, pointsLayer;

		function setRoutes(routes) {
			if (pathsLayer) {
				map.removeLayer(pathsLayer);
				pathsLayer = null;
			}
			if (pointsLayer) {
				map.removeLayer(pointsLayer);
				pointsLayer = null
			}

			// Handle empty responses
			if (!routes || !routes.length) {
				return;
			}

			var pointsFeature = {
				"type": "FeatureCollection",
				"features": []
			};
			var pathsFeature = {
				"type": "FeatureCollection",
				"features": []
			};
			for (var r = 0, R = routes.length; r < R; r++) {
				var pathCoordinates = [];
				for (var p = 0, P = routes[r].length; p < P; p++) {
					var point = routes[r][p],
					    coordinates = [point.lon, point.lat];
					point.title = point.name

					pathCoordinates.push(coordinates);
					pointsFeature.features.push({
						"type": "Feature",
						"geometry": {
							"type": "Point",
							"coordinates": coordinates
						},
						"properties": point
					});
				}
				pathsFeature.features.push({
					"type": "Feature",
					"geometry": {
						"type": "LineString",
						"coordinates": pathCoordinates
					},
					"properties": {}
				});
			}

			pathsLayer = new d3Layer(pathsFeature);
			console.log(pathsLayer, pathsFeature);
			pathsLayer.addTo(map);

			pointsLayer = mapbox.markerLayer();
			pointsLayer.setGeoJSON(pointsFeature);
			pointsLayer.addTo(map);
		}

		return {
			'map': map,
			'setRoutes': setRoutes
		};
	};
});
