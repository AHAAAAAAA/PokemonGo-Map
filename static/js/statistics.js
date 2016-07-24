var rawDataIsLoading = false;
var total = 0;

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

function processTotal(seen){
    total = 0;
    for(var i = 0; i < seen.length; i++)
        total += seen[i].count;

    document.getElementById("seen_total").innerHTML = 'Total: ' + total;
}

function processSeen(i, item) {
    //Add or update item
    if(document.getElementById("seen_" + item.pokemon_id) == null){
        //Add item
        var newItem = document.createElement('div');
        newItem.id = 'seen_' + item.pokemon_id;
        newItem.className = 'item';
        newItem.innerHTML = '   <div class="image"><img src="static/icons/' + item.pokemon_id + '.png" alt="Icon for ' + item.pokemon_name + '">\
                                </div>\
                                <div class="info">\
                                    <span class="name"><a href="http://www.pokemon.com/us/pokedex/' + item.pokemon_id + '" target="_blank" title="View in Pokedex">' + item.pokemon_name + '</a></span><br />\
                                    <span class="seen">Seen: ' + item.count + ' (' + (item.count / total * 100).toFixed(2) + '%)</span>\
                                </div>';
        document.getElementById('seen_container').appendChild(newItem);
    }else{
        //Update Item
        existingItem = document.getElementById('seen_' + item.pokemon_id);
        existingItem.getElementsByClassName('seen')[0].innerHTML = 'Seen: ' + item.count + ' (' + (item.count / total * 100).toFixed(2) + '%)';
    }
}

function cleanAndSort(seen) {
    //Clear those that aren't seen
    //var seen_pokemon = [];
    var container = document.getElementById("seen_container");

    //For now just sort by count, add column sorting in a minute
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

updatePage();
window.setInterval(updatePage, 5000);