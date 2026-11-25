package br.controleir.retornostudio;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

/** Recebe roblox-studio-auth:/?code=...&state=... e o deixa no log (lido pelo shell do Shizuku). */
public class Retorno extends Activity {
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        String url = getIntent() != null ? getIntent().getDataString() : null;
        if (url != null && url.startsWith("roblox-studio-auth:")) {
            Log.i("RetornoStudio", "URL " + url);
            Toast.makeText(this, "Login do Roblox Studio capturado. Pode voltar ao Claude.", Toast.LENGTH_LONG).show();
        }
        finish();
    }
}
