package br.controleir.bluetooth;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.os.Bundle;
import android.os.Handler;
import android.widget.TextView;

import controleir.Bluetooth;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Abre por alguns segundos (am start ... --el ms 10000 --es token X), escuta a busca BLE como app comum e grava
 * resultado-&lt;token&gt;.json na pasta do app (Android/data/br.controleir.bluetooth/files), que o shell lê.
 * A coleta e o JSON são os mesmos do leitor do shell (controleir.Bluetooth).
 */
public class Busca extends Activity {
    private BluetoothLeScanner scanner;
    private ScanCallback ouvinte;
    private boolean gravado;

    @Override
    protected void onCreate(Bundle estado) {
        super.onCreate(estado);
        final long ms = Math.max(2000, Math.min(getIntent().getLongExtra("ms", 10000), 30000));
        final String token = limpo(getIntent().getStringExtra("token"));
        TextView t = new TextView(this);
        t.setText("Controle IR: escutando aparelhos Bluetooth ao redor por " + (ms / 1000) + " s…");
        t.setTextSize(16);
        t.setPadding(56, 48, 56, 48);
        setContentView(t);
        setFinishOnTouchOutside(false);

        Bluetooth.limpar();
        final Map<String, Object> saida = new LinkedHashMap<String, Object>();
        saida.put("identidade_busca", "app");
        BluetoothAdapter a = null;
        try {
            BluetoothManager bm = (BluetoothManager) getSystemService(BLUETOOTH_SERVICE);
            a = bm != null ? bm.getAdapter() : null;
        } catch (Throwable e) {
            Bluetooth.aviso("adaptador: " + Bluetooth.causa(e));
        }
        if (a == null) {
            saida.put("erro", "este aparelho não tem Bluetooth");
            gravar(saida, token);
            return;
        }
        boolean ligado = Bluetooth.ligado(a);
        saida.put("bluetooth_ligado", ligado);
        saida.put("modo_so_ble", false);
        saida.put("pareados", Bluetooth.pareados(a));
        scanner = ligado ? Bluetooth.scanner(a) : null;
        if (scanner == null) {
            saida.put("busca", ligado ? "sem_scanner" : "bluetooth_desligado");
            gravar(saida, token);
            return;
        }
        ouvinte = new ScanCallback() {
            @Override
            public void onScanResult(int tipo, ScanResult r) {
                Bluetooth.anotar(r);
            }

            @Override
            public void onBatchScanResults(List<ScanResult> rs) {
                for (ScanResult r : rs) Bluetooth.anotar(r);
            }

            @Override
            public void onScanFailed(int codigo) {
                Bluetooth.falhaBusca = codigo;
            }
        };
        try {
            ScanSettings.Builder b = new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY);
            b.setLegacy(false);
            scanner.startScan(new ArrayList<ScanFilter>(), b.build(), ouvinte);
        } catch (Throwable e) {
            saida.put("busca", "recusada");
            saida.put("detalhe", String.valueOf(e));
            scanner = null;
            gravar(saida, token);
            return;
        }
        new Handler(getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                parar();
                saida.put("busca", Bluetooth.falhaBusca == 0 ? "ok" : "falhou");
                if (Bluetooth.falhaBusca != 0) saida.put("codigo_falha", Bluetooth.falhaBusca);
                saida.put("proximos", Bluetooth.proximos());
                gravar(saida, token);
            }
        }, ms);
    }

    private void parar() {
        if (scanner != null && ouvinte != null) {
            try {
                scanner.stopScan(ouvinte);
            } catch (Throwable e) {
                Bluetooth.aviso("parar: " + Bluetooth.causa(e));
            }
        }
        scanner = null;
    }

    @Override
    protected void onDestroy() {
        parar(); // fechada antes da hora (voltar, outra tela): não deixa a busca ligada
        super.onDestroy();
    }

    private void gravar(Map<String, Object> saida, String token) {
        if (gravado) return;
        gravado = true;
        Bluetooth.anexarAvisos(saida);
        try {
            File pasta = getExternalFilesDir(null);
            if (pasta != null) {
                File parcial = new File(pasta, "resultado-" + token + ".parcial");
                FileOutputStream f = new FileOutputStream(parcial);
                f.write(Bluetooth.json(saida).getBytes("UTF-8"));
                f.close();
                parcial.renameTo(new File(pasta, "resultado-" + token + ".json"));
            }
        } catch (Throwable e) {
            // sem onde gravar: o Controle IR percebe pela falta do arquivo
        }
        finish();
    }

    static String limpo(String t) {
        if (t == null || t.isEmpty()) return "ultimo";
        StringBuilder s = new StringBuilder();
        for (char c : t.toCharArray()) if (Character.isLetterOrDigit(c) || c == '-') s.append(c);
        return s.length() == 0 ? "ultimo" : s.toString();
    }
}
