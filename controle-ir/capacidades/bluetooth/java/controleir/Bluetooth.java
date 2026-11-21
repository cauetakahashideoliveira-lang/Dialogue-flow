package controleir;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothClass;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanRecord;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelUuid;
import android.util.SparseArray;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Busca Bluetooth pelo usuário "shell" (Shizuku + app_process): só ESCUTA os anúncios BLE ao redor e lista os
 * pareados; nunca conecta nem pareia. O Termux:API não tem Bluetooth e as ferramentas de Linux (bluetoothctl)
 * não acham o adaptador no Android; o shell tem as permissões de Bluetooth.
 *
 * Uso: app_process /system/bin controleir.Bluetooth <milissegundos> [ble]
 *   ble = com o Bluetooth desligado, tenta o modo "só BLE" (o da busca de dispositivos sempre ativa), sem ligar o
 *         Bluetooth para o usuário, e desfaz no fim.
 * Saída: uma linha JSON no stdout.
 */
public class Bluetooth {
    static final Map<String, Map<String, Object>> achados = new LinkedHashMap<String, Map<String, Object>>();
    static final List<String> avisos = new ArrayList<String>();
    static int falhaBusca = 0;
    static int lotes = 0;

    public static void main(String[] args) {
        long ms = args.length > 0 ? Long.parseLong(args[0]) : 10000;
        boolean tentarBle = args.length > 1 && "ble".equals(args[1]);
        if (Looper.getMainLooper() == null) Looper.prepareMainLooper();
        Map<String, Object> saida = new LinkedHashMap<String, Object>();
        iniciarModulos();
        BluetoothAdapter adaptador = adaptador("com.android.shell");
        if (adaptador == null) {
            saida.put("erro", "este aparelho não tem Bluetooth (ou o shell não o alcança)");
            fim(saida);
            return;
        }
        boolean ligado = ligado(adaptador);
        boolean leAntes = leLigado(adaptador);
        saida.put("bluetooth_ligado", ligado);
        boolean ligueiBle = false;
        if (!ligado && !leAntes && tentarBle) {
            ligueiBle = invocar(adaptador, "enableBLE") == Boolean.TRUE;
            for (int i = 0; ligueiBle && i < 40 && !leLigado(adaptador); i++) dormir(100);
            if (!leLigado(adaptador)) ligueiBle = false;
        }
        saida.put("modo_so_ble", ligueiBle || (!ligado && leAntes));
        saida.put("pareados", pareados(adaptador));
        // No HyperOS (POCO, 21/11) a busca do com.android.shell é recusada calada: ScanController.checkAllowedToScan
        // só deixa pacotes do sistema (uid < 10000) buscarem com uma tela própria em primeiro plano, e o Shell não tem
        // nenhuma. Sem nome de pacote a regra passa, mas o serviço quebra adiante (NullPointerException). O Python
        // reconhece a recusa pelo registro do sistema. O Android puro não tem essa regra.
        final BluetoothLeScanner scanner = (ligado || leLigado(adaptador)) ? scanner(adaptador) : null;
        if (scanner == null) {
            saida.put("busca", ligado ? "sem_scanner" : "bluetooth_desligado");
            if (ligueiBle) invocar(adaptador, "disableBLE");
            fim(saida);
            return;
        }
        final ScanCallback ouvinte = new ScanCallback() {
            @Override
            public void onScanResult(int tipo, ScanResult r) {
                anotar(r);
            }

            @Override
            public void onBatchScanResults(List<ScanResult> rs) {
                lotes++;
                for (ScanResult r : rs) anotar(r);
            }

            @Override
            public void onScanFailed(int codigo) {
                falhaBusca = codigo;
            }
        };
        try {
            ScanSettings.Builder b = new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY);
            try {
                b.setLegacy(false); // também os anúncios estendidos (Bluetooth 5)
            } catch (Throwable t) {
                // Android antigo
            }
            scanner.startScan(new ArrayList<ScanFilter>(), b.build(), ouvinte);
        } catch (Throwable t) {
            saida.put("busca", "recusada");
            saida.put("detalhe", String.valueOf(t));
            if (ligueiBle) invocar(adaptador, "disableBLE");
            fim(saida);
            return;
        }
        final Map<String, Object> s = saida;
        final BluetoothAdapter a = adaptador;
        final boolean desfazer = ligueiBle;
        new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
            @Override
            public void run() {
                try {
                    scanner.stopScan(ouvinte);
                } catch (Throwable t) {
                    aviso("parar: " + t);
                }
                if (desfazer) invocar(a, "disableBLE");
                s.put("busca", falhaBusca == 0 ? "ok" : "falhou");
                if (falhaBusca != 0) s.put("codigo_falha", falhaBusca);
                s.put("proximos", new ArrayList<Object>(achados.values()));
                fim(s);
            }
        }, ms);
        Looper.loop();
    }

    // ------------------------------------------------------------------ adaptador
    static void iniciarModulos() {
        // No app_process não há Context: a identidade do pedido (AttributionSource) precisa dizer que é o shell,
        // senão a checagem de permissão do Android 12+ recusa. Sem a API escondida, cai no getDefaultAdapter.
        // Num app quem registra o serviço do Bluetooth é o ActivityThread (initializeMainlineModules); no
        // app_process ninguém faz isso e o createAdapter devolve null calado (visto no POCO, Android 16, 21/11).
        try {
            Class.forName("android.app.ActivityThread").getMethod("initializeMainlineModules").invoke(null);
        } catch (Throwable t) {
            aviso("módulos: " + causa(t));
            try {
                Class<?> gerente = Class.forName("android.os.BluetoothServiceManager");
                Class.forName("android.bluetooth.BluetoothFrameworkInitializer")
                        .getMethod("setBluetoothServiceManager", gerente).invoke(null, gerente.newInstance());
            } catch (Throwable t2) {
                aviso("serviço do Bluetooth: " + causa(t2));
            }
        }
    }

    /** pacote null = identidade só pelo uid (sem nome de pacote). */
    static BluetoothAdapter adaptador(String pacote) {
        try {
            Class<?> fonte = Class.forName("android.content.AttributionSource$Builder");
            Object construtor = fonte.getConstructor(int.class).newInstance(android.os.Process.myUid());
            if (pacote != null) fonte.getMethod("setPackageName", String.class).invoke(construtor, pacote);
            Object atrib = fonte.getMethod("build").invoke(construtor);
            Method criar = BluetoothAdapter.class.getDeclaredMethod("createAdapter",
                    Class.forName("android.content.AttributionSource"));
            criar.setAccessible(true);
            Object a = criar.invoke(null, atrib);
            if (a != null) return (BluetoothAdapter) a;
            aviso("createAdapter devolveu null (" + pacote + ")");
        } catch (Throwable t) {
            aviso("identidade " + pacote + ": " + causa(t));
        }
        if (pacote == null) return null;
        try {
            BluetoothAdapter a = BluetoothAdapter.getDefaultAdapter();
            if (a == null) aviso("getDefaultAdapter devolveu null");
            return a;
        } catch (Throwable t) {
            aviso("adaptador: " + causa(t));
            return null;
        }
    }

    static boolean ligado(BluetoothAdapter a) {
        try {
            return a.isEnabled();
        } catch (Throwable t) {
            aviso("estado: " + causa(t));
            return false;
        }
    }

    static boolean leLigado(BluetoothAdapter a) {
        return invocar(a, "isLeEnabled") == Boolean.TRUE;
    }

    static BluetoothLeScanner scanner(BluetoothAdapter a) {
        try {
            return a.getBluetoothLeScanner();
        } catch (Throwable t) {
            aviso("scanner: " + causa(t));
            return null;
        }
    }

    static Object invocar(Object alvo, String metodo) {
        try {
            Method m = alvo.getClass().getMethod(metodo);
            m.setAccessible(true);
            return m.invoke(alvo);
        } catch (Throwable t) {
            aviso(metodo + ": " + causa(t));
            return null;
        }
    }

    // ------------------------------------------------------------------ dados
    static List<Object> pareados(BluetoothAdapter a) {
        List<Object> lista = new ArrayList<Object>();
        try {
            Set<BluetoothDevice> ds = a.getBondedDevices();
            if (ds == null) return lista;
            for (BluetoothDevice d : ds) {
                Map<String, Object> m = new LinkedHashMap<String, Object>();
                m.put("endereco", d.getAddress());
                m.put("nome", nome(d));
                m.put("tipo_radio", tipoRadio(d));
                try {
                    BluetoothClass c = d.getBluetoothClass();
                    if (c != null) {
                        m.put("classe_maior", c.getMajorDeviceClass());
                        m.put("classe", c.getDeviceClass());
                    }
                } catch (Throwable t) {
                    // sem permissão para a classe: segue sem ela
                }
                lista.add(m);
            }
        } catch (Throwable t) {
            aviso("pareados: " + causa(t));
        }
        return lista;
    }

    static String nome(BluetoothDevice d) {
        try {
            return d.getName();
        } catch (Throwable t) {
            return null;
        }
    }

    static String tipoRadio(BluetoothDevice d) {
        try {
            switch (d.getType()) {
                case 1: return "classico";
                case 2: return "ble";
                case 3: return "duplo";
                default: return "desconhecido";
            }
        } catch (Throwable t) {
            return null;
        }
    }

    static synchronized void anotar(ScanResult r) {
        BluetoothDevice d = r.getDevice();
        if (d == null) return;
        String end = d.getAddress();
        Map<String, Object> m = achados.get(end);
        if (m == null) {
            m = new LinkedHashMap<String, Object>();
            m.put("endereco", end);
            m.put("vezes", 0);
            m.put("rssi_max", -999);
            achados.put(end, m);
        }
        m.put("vezes", (Integer) m.get("vezes") + 1);
        m.put("rssi", r.getRssi());
        if (r.getRssi() > (Integer) m.get("rssi_max")) m.put("rssi_max", r.getRssi());
        try {
            m.put("conectavel", r.isConnectable());
            if (r.getTxPower() != 127) m.put("tx", r.getTxPower()); // 127 = não informado
        } catch (Throwable t) {
            // Android antigo
        }
        ScanRecord sr = r.getScanRecord();
        String n = sr != null ? sr.getDeviceName() : null;
        if (n == null || n.isEmpty()) n = nome(d);
        if (n != null && !n.isEmpty()) m.put("nome", n);
        if (sr == null) return;
        if (sr.getTxPowerLevel() > -128 && sr.getTxPowerLevel() < 127) m.put("tx_anunciado", sr.getTxPowerLevel());
        SparseArray<byte[]> fab = sr.getManufacturerSpecificData();
        if (fab != null && fab.size() > 0) {
            List<Object> l = new ArrayList<Object>();
            for (int i = 0; i < fab.size(); i++) {
                Map<String, Object> f = new LinkedHashMap<String, Object>();
                f.put("id", fab.keyAt(i));
                f.put("dados", hex(fab.valueAt(i), 24));
                l.add(f);
            }
            m.put("fabricante", l);
        }
        List<ParcelUuid> us = sr.getServiceUuids();
        Map<ParcelUuid, byte[]> sd = sr.getServiceData();
        List<Object> servicos = new ArrayList<Object>();
        if (us != null) for (ParcelUuid u : us) servicos.add(curto(u));
        if (sd != null) for (ParcelUuid u : sd.keySet()) if (!servicos.contains(curto(u))) servicos.add(curto(u));
        if (!servicos.isEmpty()) m.put("servicos", servicos);
    }

    /** UUID de 16 bits ("180d") quando é do padrão Bluetooth; senão o UUID inteiro. */
    static String curto(ParcelUuid u) {
        String s = u.toString().toLowerCase();
        if (s.startsWith("0000") && s.endsWith("-0000-1000-8000-00805f9b34fb")) return s.substring(4, 8);
        return s;
    }

    static String hex(byte[] b, int max) {
        if (b == null) return "";
        StringBuilder s = new StringBuilder();
        for (int i = 0; i < b.length && i < max; i++) s.append(String.format("%02x", b[i] & 0xff));
        return s.toString();
    }

    static void aviso(String a) {
        if (!avisos.contains(a) && avisos.size() < 20) avisos.add(a);
    }

    static String causa(Throwable t) {
        while (t.getCause() != null) t = t.getCause();
        String s = t.getClass().getSimpleName() + (t.getMessage() != null ? ": " + t.getMessage() : "");
        return s.length() > 200 ? s.substring(0, 200) : s;
    }

    static void dormir(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // ------------------------------------------------------------------ JSON (sem dependências)
    static void fim(Map<String, Object> saida) {
        if (!avisos.isEmpty()) saida.put("avisos", avisos);
        System.out.println(json(saida));
        System.out.flush();
        System.exit(0);
    }

    static String json(Object o) {
        StringBuilder s = new StringBuilder();
        escrever(s, o);
        return s.toString();
    }

    @SuppressWarnings("unchecked")
    static void escrever(StringBuilder s, Object o) {
        if (o == null) {
            s.append("null");
        } else if (o instanceof Boolean || o instanceof Integer || o instanceof Long) {
            s.append(o);
        } else if (o instanceof Map) {
            s.append('{');
            boolean primeiro = true;
            for (Map.Entry<String, Object> e : ((Map<String, Object>) o).entrySet()) {
                if (!primeiro) s.append(',');
                primeiro = false;
                texto(s, e.getKey());
                s.append(':');
                escrever(s, e.getValue());
            }
            s.append('}');
        } else if (o instanceof List) {
            s.append('[');
            boolean primeiro = true;
            for (Object x : (List<Object>) o) {
                if (!primeiro) s.append(',');
                primeiro = false;
                escrever(s, x);
            }
            s.append(']');
        } else {
            texto(s, String.valueOf(o));
        }
    }

    static void texto(StringBuilder s, String t) {
        s.append('"');
        for (int i = 0; i < t.length(); i++) {
            char c = t.charAt(i);
            if (c == '"' || c == '\\') s.append('\\').append(c);
            else if (c < 0x20) s.append(String.format("\\u%04x", (int) c));
            else s.append(c);
        }
        s.append('"');
    }
}
