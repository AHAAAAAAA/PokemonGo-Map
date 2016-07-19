package com.pokemapp;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
import java.util.Map;

public class MyFBMS extends FirebaseMessagingService {

    @Override
    public void onMessageReceived(final RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);

        Map<String, String> data = remoteMessage.getData();
        System.out.println(data);

        Pokemon pokemon = new Pokemon(data.get("pokename"), Integer.parseInt(data.get("pokeId")), Double.parseDouble(data.get("lat")), Double.parseDouble(data.get("lon")),
              Double.valueOf(data.get("hiddens")).longValue());
        ((MyApplication) getApplication()).s.onNext(
              pokemon);
    }
}
