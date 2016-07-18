var setLabelTime = function() {
	$('.label-countdown').each(function(e) {
		var time = $(this).data('disappears-at');
		var timestring = "";
		var disappearsAt = new Date(parseInt(time) * 1000);
		if (true) { // difference between disappears-at time and now. Negative if passed
			var now = new Date();
			var difference = Math.abs(disappearsAt - now);
			var hours = Math.floor(difference / 36e5);
			var minutes = Math.floor((difference - (hours * 36e5)) / 6e4);
			var seconds = Math.floor((difference - (hours * 36e5) - (minutes * 6e4)) / 1e3);

			if (disappearsAt < now) {
				timestring += "-";
				$(this).remove()
			}

			if (hours > 0) {
				timestring += hours + ":";
			}

			timestring += ("0" + minutes).slice(-2) + ":";
			timestring += ("0" + seconds).slice(-2);
		} else { // set label to disappears-at time
			var hours = disappearsAt.getHours();
			var minutes = disappearsAt.getMinutes();
			if (minutes < 10) {
				minutes = "0" + minutes;
			}

			var seconds = disappearsAt.getSeconds();
			if (seconds < 10) {
				seconds = "0" + seconds;
			}
			timestring += hours + ":" + minutes + ":" + seconds;
		}
		$(this).text(timestring)
	});
};

setInterval(setLabelTime, 1000);
