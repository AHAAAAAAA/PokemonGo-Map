$(function(){

	var $useLoc = $('#use-loc');
	$useLoc.prop('checked', localStorage.useLoc === 'true');
	$useLoc.change(function() {
		localStorage.useLoc = $useLoc.is(':checked');
	});

	var tm;
	var $timer = $('#use-timer');
	$timer.prop('checked', localStorage.useTimer === 'true');
	$timer.change(function() {
		localStorage.useTimer = $timer.is(':checked');
		if (localStorage.useTimer === 'false') {
			clearTimeout(tm);
		}
		else {
			clearTimeout(tm);
			updateTimes();
		}
	});

	$('#nav button').click(function() {
		if (localStorage.useLoc !== 'true') {
			return (location.href="/mobile");
		}
		else if ("geolocation" in navigator) {
			navigator.geolocation.getCurrentPosition(function(p) {
				location.href='/mobile?lat='+p.coords.latitude+'&lon='+p.coords.longitude;
			}, function(err) {
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
	});

	function updateTimes() {
		// server tells us how many seconds are left we note the
		// pageload time and count down from there.
		// Yes, this could be a smidge innaccurate, but not by
		// more than 1 second or so which doesn't matter.
		// And now we don't have to deal with timestamps and dates!
		$('div.remain').each(function(idx, element){
			var now = new Date().getTime();
			var secondsPassed = Math.floor((now - page_loaded)/1000);
			var alivefor =  $(element).data('disappear');
			var remain = alivefor - secondsPassed;
			var min = Math.floor(remain / 60);
			var sec = remain % 60;
			$(element).text(remain > 0 ? min + ' min ' + sec + ' sec' : '(expired)');
		});
		tm = setTimeout(updateTimes, 1000);
	};
	if (localStorage.useTimer === 'true') {
		updateTimes();
	}

	$("li").click(function() {
		window.document.location = $(this).data("href");
	});

});
