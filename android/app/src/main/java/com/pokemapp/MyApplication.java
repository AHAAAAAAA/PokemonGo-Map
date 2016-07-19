package com.pokemapp;

import android.app.Application;
import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;
import rx.Observable;
import rx.functions.Action1;
import rx.subjects.PublishSubject;

public class MyApplication extends Application {

    PublishSubject<Pokemon> s = PublishSubject.create();

    private Set<Pokemon> poks = new HashSet<>();

    public Observable<Pokemon> poks() {
        return s.doOnNext(new Action1<Pokemon>() {
            @Override
            public void call(final Pokemon pokemon) {
                if (!poks.contains(pokemon)) {
                    NotificationManager systemService = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

                    Notification no = new Notification.Builder(MyApplication.this)
                          .setContentTitle(pokemon.name)
                          .setContentText(pokemon.timeS.toString("HH:mm:ss"))
                          .setSmallIcon(getResources().getIdentifier("p_" + pokemon.id, "drawable", getPackageName()))
                          .setLargeIcon(a("p_" + pokemon.id))
                          .setDefaults(Notification.DEFAULT_ALL)
                          .build();

                    //systemService.notify((int) (Math.random() * 1000000), no);
                }
            }
        }).doOnNext(new Action1<Pokemon>() {
            @Override
            public void call(final Pokemon pokemon) {
                synchronized (poks) {
                    poks.add(pokemon);
                    Iterator<Pokemon> iterator = poks.iterator();
                    while (iterator.hasNext()) {
                        if (iterator.next().timeS.isBeforeNow()) {
                            iterator.remove();
                        }
                    }
                }
            }
        })
              .startWith(poks);
    }

    private Bitmap a(String name) {
        Resources resources = getResources();
        final int resourceId = resources.getIdentifier(name, "drawable",
              getPackageName());
        return BitmapFactory.decodeResource(resources, resourceId);
    }
}
