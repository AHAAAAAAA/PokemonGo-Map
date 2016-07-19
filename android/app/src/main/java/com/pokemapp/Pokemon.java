package com.pokemapp;

import org.joda.time.DateTime;

public class Pokemon {

    final String name;
    final int id;
    final double lat;
    final double lon;
    final DateTime timeS;

    public Pokemon(final String name, final int id, final double lat, final double lon, final long timeS) {
        this.name = name;
        this.id = id;
        this.lat = lat;
        this.lon = lon;
        this.timeS = new DateTime(timeS * 1000);
    }

    @Override
    public boolean equals(final Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Pokemon pokemon = (Pokemon) o;

        if (id != pokemon.id) return false;
        if (Double.compare(pokemon.lat, lat) != 0) return false;
        if (Double.compare(pokemon.lon, lon) != 0) return false;
        return name.equals(pokemon.name);
    }

    @Override
    public int hashCode() {
        int result;
        long temp;
        result = name.hashCode();
        result = 31 * result + id;
        temp = Double.doubleToLongBits(lat);
        result = 31 * result + (int) (temp ^ temp >>> 32);
        temp = Double.doubleToLongBits(lon);
        result = 31 * result + (int) (temp ^ temp >>> 32);
        return result;
    }
}
