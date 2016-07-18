var setLabelTime = function(){
    $('.label-countdown').each(function(e){
        var disappearsAt = new Date(parseInt($(this).data('disappears-at'))*1000);
        var now = new Date();
        var timestring = "";

        var difference = Math.abs(disappearsAt - now);
        var hours = Math.floor(difference / 36e5);
        var minutes = Math.floor((difference - (hours * 36e5)) / 6e4);
        var seconds = Math.floor((difference - (hours * 36e5) - (minutes * 6e4)) / 1e3);
        
        if(disappearsAt < now){
            timestring = "expired";
        } 
        else {
            if(hours > 0){
                timestring += hours + "h";
            }
            timestring += ("0" + minutes).slice(-2) + "m";
            timestring += ("0" + seconds).slice(-2) + "s";
            timestring = "disappears in " + timestring;
        }

        $(this).text(timestring)
    });
};

setInterval(setLabelTime, 1000);