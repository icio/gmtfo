define(["mapbox", "leaflet.d3"], function(L, D3Layer)
{
	L = window.L; // FIXME Requirejs isn't being setup correctly for mapbox/leaflet

	return function(e, mapId)
	{
		var map = L.mapbox.map(e, mapId, {
			'legendControl': false
		});
		map.zoomControl.removeFrom(map);
		// map.dragging.disable();
		// map.touchZoom.disable();
		// map.doubleClickZoom.disable();
		// map.scrollWheelZoom.disable();

		var pathsLayer, pointsLayer;

		function setRoutes(routes) {
			// Remove old layers
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

			pathsLayer = new L.LayerGroup().addTo(map);

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
					point.title = point.name+", "+point.city+", "+point.country;
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

				// Force RHR
				pathCoordinates.sort(function(a, b) {
					var left = a[0] < b[0], above = a[1] > b[1], A=1, B=-1;

					// if (left) {
					// 	console.log("a", a, "left of", "b", b);
					// } else {
					// 	console.log("a", a, "right of", "b", b);
					// }
					// if (above) {
					// 	console.log("a", a, "above", "b", b);
					// } else {
					// 	console.log("a", a, "below", "b", b);
					// }

					var r = (above
						?(left ? A : A)
						:(left ? B : B)
					)
					// console.log("choosing", r == -1 ? "b":"a");
					return r;
				});

				pathsLayer.addLayer(new D3Layer([{
					"type": "Feature",
					"geometry": {
						"type": "LineString",
						"coordinates": pathCoordinates
					},
					"properties": {}
				}], {"pathClass": "route"}));
			}

			pointsLayer = L.mapbox.markerLayer();
			pointsLayer.setGeoJSON(pointsFeature);
			pointsLayer.addTo(map);
		}

		return {
			'map': map,
			'setRoutes': setRoutes
		};
	};
});
