var loadingMessage = document.getElementById('msg');

var useLoc = document.getElementById('use-loc');
useLoc.checked = localStorage.useLoc === 'true';
useLoc.onchange = function() {
	localStorage.useLoc = useLoc.checked;
};

var tm;
var useTimer = document.getElementById('use-timer');
useTimer.checked = localStorage.useTimer !== 'false';
useTimer.onchange = function() {
	localStorage.useTimer = useTimer.checked;
	if (localStorage.useTimer === 'false') {
		clearTimeout(tm);
	}
	else {
		clearTimeout(tm);
		updateTimes();
	}
};

document.querySelector('#nav button').onclick = function() {
	if (localStorage.useLoc !== 'true') {
		return (location.href="/mobile");
	}
	else if ("geolocation" in navigator) {

		// Getting the GPS position can be very slow on some devices
		loadingMessage.innerText='Getting location...';
		navigator.geolocation.getCurrentPosition(function(p) {
			loadingMessage.innerText='Reloading...';
			location.href='/mobile?lat='+p.coords.latitude+'&lon='+p.coords.longitude;

		}, function(err) {
			loadingMessage.innerText='';
			alert('Failed to get location: ' + err.message);

		}, {
			enableHighAccuracy: true,
			timeout: 5000,
			maximumAge: 5000
		});
	}
	else {
		alert('Your device does not support web geolocation');
	}
};

function updateTimes() {
	// server tells us how many seconds are left we note the
	// pageload time and count down from there.
	// Yes, this could be a smidge innaccurate, but not by
	// more than 1 second or so which doesn't matter.
	// And now we don't have to deal with timestamps and dates!
	document.querySelectorAll('div.remain').forEach(function(element){
		var now = new Date().getTime();
		var secondsPassed = Math.floor((now - page_loaded)/1000);
		var alivefor =  element.getAttribute('disappear');
		var remain = alivefor - secondsPassed;
		var min = Math.floor(remain / 60);
		var sec = remain % 60;
		element.innerText = (remain > 0) ? min + ' min ' + sec + ' sec' : '(expired)';
	});
	tm = setTimeout(updateTimes, 1000);
};
if (localStorage.useTimer !== 'false') {
	updateTimes();
}

document.querySelectorAll("li").forEach(function(listItem) {
	listItem.onclick = function() {
		window.document.location = this.getAttribute('href');
	};
});
