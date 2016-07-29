function countMarkers() {
	document.getElementById("stats-pkmn-label").innerHTML = "Pokémons";
	document.getElementById("stats-gym-label").innerHTML = "Gyms";
	document.getElementById("stats-pkstop-label").innerHTML = "PokéStops";
	
	var arenaCount = [];
	var arenaTotal = 0;
	var pkmnCount = [];
	var pkmnTotal = 0;
	var pokestopCount = [];
	var pokestopTotal = 0;
	if(Store.get('showPokemon'))
	{
		$.each(map_data.pokemons, function(key, value) {
			if (pkmnCount[map_data.pokemons[key]['pokemon_id']] == 0 || pkmnCount[map_data.pokemons[key]['pokemon_id']] == null )
			{
				pkmnCount[map_data.pokemons[key]['pokemon_id']] = {
					"ID": map_data.pokemons[key]['pokemon_id'],
					"Count": 1,
					"Name": map_data.pokemons[key]['pokemon_name']
				};
			}
			else
			{
				pkmnCount[map_data.pokemons[key]['pokemon_id']].Count += 1;
			}
			pkmnTotal++;
		});
		pkmnCount.sort(sort_by('Name', false));
		$.each(map_data.pokemons, function(key, value) {
			var pkmnListString = "<table><thead><tr><th>Icon</th><th>Name</th><th>Count</th><th>%</th></tr></thead><tbody><tr><td></td><td>Total</td><td>"+pkmnTotal+"</td><td></td></tr>";
			for(var i=0;i < pkmnCount.length;i++) {
				if (pkmnCount[i] != null && pkmnCount[i].Count > 0)
				{
					pkmnListString += "<tr><td><img src=\"/static/icons/" + pkmnCount[i].ID + ".png\" /></td><td><a href='http://www.pokemon.com/us/pokedex/" + pkmnCount[i].ID + "' target='_blank' title='View in Pokedex' style=\"color: black;\">" + pkmnCount[i].Name + "</a></td><td>" + pkmnCount[i].Count + "</td><td>"+Math.round(pkmnCount[i].Count*100/pkmnTotal*10)/10+"%</td></tr>";
				}
			}
			pkmnListString += "</tbody></table>";
			document.getElementById("pokemonList").innerHTML = pkmnListString;
		});
	}
	else
	{
		document.getElementById("pokemonList").innerHTML = "Pokémons markers are disabled";;
	}
	if(Store.get('showGyms'))
	{
		$.each(map_data.gyms, function(key, value) {
			if (arenaCount[map_data.gyms[key]['team_id']] == 0 || arenaCount[map_data.gyms[key]['team_id']] == null )
			{
				arenaCount[map_data.gyms[key]['team_id']] = 1;
			}
			else
			{
				arenaCount[map_data.gyms[key]['team_id']] += 1;
			}
			arenaTotal++;
			var arenaListString = "<table><th>Icon</th><th>Team Color</th><th>Count</th><th>%</th><tr><td></td><td>Total</td><td>"+arenaTotal+"</td></tr>";
			for(var i=0;i < arenaCount.length;i++) {
				if (arenaCount[i] > 0)
				{
					if(i == 1)
					{
						arenaListString += "<tr><td><img src=\"/static/forts/Mystic.png\" /></td><td>" + "Blue" + "</td><td>" + arenaCount[i] + "</td><td>"+Math.round(arenaCount[i]*100/arenaTotal*10)/10+"%</td></tr>";
					}
					else if(i == 2)
					{
						arenaListString += "<tr><td><img src=\"/static/forts/Valor.png\" /></td><td>" + "Red" + "</td><td>" + arenaCount[i] + "</td><td>"+Math.round(arenaCount[i]*100/arenaTotal*10)/10+"%</td></tr>";
					}
					else if(i == 3)
					{
						arenaListString += "<tr><td><img src=\"/static/forts/Instinct.png\" /></td><td>" + "Yellow" + "</td><td>" + arenaCount[i] + "</td><td>"+Math.round(arenaCount[i]*100/arenaTotal*10)/10+"%</td></tr>";
					}
					else
					{
						arenaListString += "<tr><td><img src=\"/static/forts/Uncontested.png\" /></td><td>" + "Clear" + "</td><td>" + arenaCount[i] + "</td><td>"+Math.round(arenaCount[i]*100/arenaTotal*10)/10+"%</td></tr>";
					}
				}
			}
			arenaListString += "</table>";
			document.getElementById("arenaList").innerHTML = arenaListString;
		});
	}
	else
	{
		document.getElementById("arenaList").innerHTML = "Gyms markers are disabled";
	}
	if(Store.get('showPokestops'))
	{
		$.each(map_data.pokestops, function(key, value) {
			var pokestopLured = false;
			if(map_data.pokestops[key]['lure_expiration'] != null && map_data.pokestops[key]['lure_expiration'] > 0)
			{
				if (pokestopCount[1] == 0 || pokestopCount[1] == null )
				{
					pokestopCount[1] = 1;
				}
				else
				{
					pokestopCount[1] += 1;
				}
			}
			else
			{
				if (pokestopCount[0] == 0 || pokestopCount[0] == null )
				{
					pokestopCount[0] = 1;
				}
				else
				{
					pokestopCount[0] += 1;
				}
			}
			pokestopTotal++;
			var pokestopListString = "<table><th>Icon</th><th>Status</th><th>Count</th><th>%</th><tr><td></td><td>Total</td><td>"+pokestopTotal+"</td></tr>";
			for(var i=0;i < pokestopCount.length;i++) {
				if (pokestopCount[i] > 0)
				{
					if(i == 0)
					{
						pokestopListString += "<tr><td><img src=\"/static/forts/Pstop.png\" /></td><td>" + "Not Lured" + "</td><td>" + pokestopCount[i] + "</td><td>"+Math.round(pokestopCount[i]*100/pokestopTotal*10)/10+"%</td></tr>";
					}
					else if(i == 1)
					{
						pokestopListString += "<tr><td><img src=\"/static/forts/PstopLured.png\" /></td><td>" + "Lured" + "</td><td>" + pokestopCount[i] + "</td><td>"+Math.round(pokestopCount[i]*100/pokestopTotal*10)/10+"%</td></tr>";
					}
				}
			}
			pokestopListString += "</table>";
			document.getElementById("pokestopList").innerHTML = pokestopListString;
		});
	}
	else
	{
		document.getElementById("pokestopList").innerHTML = "PokéStops markers are disabled";
	}
};

var sort_by = function(field, reverse, primer){
    var key = primer ? 
        function(x) {return primer(x[field])} : 
        function(x) {return x[field]};

    reverse = !reverse ? 1 : -1;

    return function (a, b) {
        return a = key(a), b = key(b), reverse * ((a > b) - (b > a));
    } 
}
