var rawDataIsLoading = false;
var detailsLoading = false;
var total = 0;
var detailInterval = null;
var pokemonid = 0;
var lastappearance = 1;

function loadRawData(){
    return $.ajax({
        url: "raw_data",
        type: 'GET',
        data: {
            'pokemon': false,
            'pokestops': false,
            'gyms': false,
            'scanned': false,
            'seen': true,
            'duration': document.getElementById('duration').options[document.getElementById('duration').selectedIndex].value
        },
        dataType: "json",
        beforeSend: function() {
            if (rawDataIsLoading) {
                return false;
            } else {
                rawDataIsLoading = true;
            }
        },
        complete: function() {
            rawDataIsLoading = false;
        }
    })
}

function loadDetails(){
    return $.ajax({
        url: "raw_data",
        type: 'GET',
        data: {
            'pokemon': false,
            'pokestops': false,
            'gyms': false,
            'scanned': false,
            'appearances': true,
            'pokemonid': pokemonid,
            'last': lastappearance
        },
        dataType: "json",
        beforeSend: function() {
            if (detailsLoading) {
                return false;
            } else {
                detailsLoading = true;
            }
        },
        complete: function() {
            detailsLoading = false;
        }
    })
}

function processTotal(seen){
    total = 0;
    for(var i = 0; i < seen.length; i++)
        total += seen[i].count;

    document.getElementById("seen_total").innerHTML = 'Total: ' + total.toLocaleString();
}

function processSeen(i, item) {
    var monthArray = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var percentage = (item.count / total * 100).toFixed(2);
    var lastSeen = new Date(item.disappear_time);
    lastSeen =  lastSeen.getHours() + ':' +
                ("0" + lastSeen.getMinutes()).slice(-2) + ':' +
                ("0" + lastSeen.getSeconds()).slice(-2) + ' ' +
                lastSeen.getDate() + ' ' +
                monthArray[lastSeen.getMonth()] + ' ' +
                lastSeen.getFullYear();
    var location = (item.latitude * 1).toFixed(7) + ', ' + (item.longitude * 1).toFixed(7);
    var element = document.getElementById("seen_" + item.pokemon_id);
    if(element == null){
        element = document.createElement('div');
        element.id = 'seen_' + item.pokemon_id;
        element.className = 'item';
        element.innerHTML = '   <div class="container">\
                                    <div class="image">\
                                        <img src="static/icons/' + item.pokemon_id + '.png"\
                                             alt="Icon for ' + item.pokemon_name + '"\
                                        >\
                                    </div>\
                                    <div class="info">\
                                        <span class="name">\
                                            <a href="http://www.pokemon.com/us/pokedex/' + item.pokemon_id + '" \
                                               target="_blank" \
                                               title="View in Pokedex"\
                                            >' + item.pokemon_name + '</a>\
                                        </span>\
                                        <br />\
                                        <span class="seen"></span>\
                                    </div>\
                                </div>\
                                <div class="details">\
                                    <span class="lastseen"></span><br />\
                                    <span class="location"></span><br />\
                                    <a href="#" onclick="return showDetails(this.parentElement.parentElement);">More Locations</a>\
                                </div>';
        document.getElementById('seen_container').appendChild(element);
    }
    element.getElementsByClassName('seen')[0].innerHTML = 'Seen: ' + item.count.toLocaleString() + ' (' + percentage + '%)';
    element.getElementsByClassName('lastseen')[0].innerHTML = 'Last Seen: ' + lastSeen;
    element.getElementsByClassName('location')[0].innerHTML = 'Location: ' + location;
}

function cleanAndSort(seen) {
    //Clear those that aren't seen
    var container = document.getElementById("seen_container");

    seen.sort(function(a, b){
        var sort = document.getElementById("sort");
        var order = document.getElementById("order");

        if(order.options[order.selectedIndex].value == "desc"){
            var tmp = b;
            b = a;
            a = tmp;
        }

        if(sort.options[sort.selectedIndex].value == "id"){
            return a.pokemon_id-b.pokemon_id;
        }else if(sort.options[sort.selectedIndex].value == "name"){
            if(a.pokemon_name.toLowerCase() < b.pokemon_name.toLowerCase()) return 1;
            if(a.pokemon_name.toLowerCase() > b.pokemon_name.toLowerCase()) return -1;
            return 0;
        }else{
            //Default to count
            if(a.count == b.count) //Same count: order by id
                return b.pokemon_id-a.pokemon_id;

            return a.count-b.count;
        }

    });

    //Order all existing
    for(var i = seen.length - 1; i >= 0; i--){
        var node = document.getElementById('seen_' + seen[i].pokemon_id);
        container.insertBefore(node, container.childNodes[0]);
    }

    //Remove any unneeded items
    for(var i = seen.length; i < container.childNodes.length; i++){
        var node = container.childNodes[i];
        container.removeChild(node);
        i--;
    }
}

function updatePage(){
    loadRawData().done(function (result) {
        processTotal(result.seen);
        $.each(result.seen, processSeen);
        cleanAndSort(result.seen);
    });

    var duration = document.getElementById("duration");
    document.getElementById("seen_header").innerHTML = 'Pokemon Seen in ' + duration.options[duration.selectedIndex].text;
}

function processAppearance(i, appearance){
    var monthArray = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var saw = new Date(appearance.disappear_time);
    var detailContainer = document.getElementById("location_content");
    detailContainer.innerHTML = saw.getHours() + ":" +
                                ("0" + saw.getMinutes()).slice(-2) + ":" +
                                ("0" + saw.getSeconds()).slice(-2) + " " +
                                saw.getDate() + " " +
                                monthArray[saw.getMonth()] + " " +
                                saw.getFullYear() + " at " +
                                (appearance.latitude).toFixed(7) + ", " +
                                (appearance.longitude).toFixed(7) +
                                '<br />' + detailContainer.innerHTML;
    lastappearance = Math.max(lastappearance, appearance.disappear_time);
}

function updateDetails(){
    loadDetails().done(function (result) {
        $.each(result.appearances, processAppearance)
    });
}

function showDetails(container){
    lastappearance = 0;
    document.getElementById("location_details").style.display = "block";
    pokemonid = container.id.replace(/^seen_/g, '');
    document.getElementById("location_header").innerHTML = 'Appearances of ' +
                                                            container.getElementsByClassName("name")[0].innerHTML +
                                                            '(#' + pokemonid + ')';
    document.getElementById("location_content").innerHTML = '';
    detailInterval = window.setInterval(updateDetails, 5000);
    updateDetails();
    return false;
}

function closeOverlay(){
    document.getElementById("location_details").style.display = "none";
    window.clearInterval(detailInterval)
    return false;
}

updatePage();
window.setInterval(updatePage, 5000);