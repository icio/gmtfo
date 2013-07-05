requirejs.config({
	baseUrl: "static/scripts/",
	paths: {
		"jquery": "jquery-2.0.2.min",
		"angular": "angular-1.0.7.min",
		"bootstrap": "bootstrap-2.3.2.min",
		"lessjs": "less-1.4.1.min",
		"mapbox": "mapbox-1.2.0.min",
		"leaflet-d3": "leaflet-d3-147a943",
		"d3": "d3-v3.min",
	},
	shim: {
		// External lib setup
		'jquery': { 'exports': '$' },
		'bootstrap': { 'deps': ['jquery'] },
		'angular': { 'deps': ['jquery'], 'exports': 'angular' },
		'd3': { 'exports': 'd3' },
		'mapbox': { 'exports': 'L' },
		'leaflet-d3': { 'deps': ['mapbox', 'd3'], 'exports': 'L.GeoJSON.d3' },
		
		// Force module loading:
		'gmtfo/main': { 'deps': [
			'bootstrap',
			'lessjs'
		]}
	},

	// Cache-busting:
	urlArgs: "bust=" + (new Date()).getTime()
});

requirejs(["gmtfo/main"]);
