package controleir;

import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.UiAutomation;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.SystemClock;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

/**
 * Leitor e operador de tela rápido do controle-ir. Roda como usuário "shell" (Shizuku → app_process) e conversa
 * pela entrada padrão: cada linha é "ID COMANDO [args]"; a resposta vai para PASTA/ID.r (escrita atômica).
 *
 * Por que existe: o `uiautomator dump` espera a tela ficar parada (1 s de calma, até 10 s) e abre uma conexão nova a
 * cada vez; aqui a conexão com a acessibilidade fica aberta e a leitura é imediata. Os toques são injetados direto
 * (sem abrir o processo `input` a cada toque) e o texto vai pelo campo em foco (acentos funcionam).
 *
 * Comandos: ping | dump | foco | tocar X Y [ms] | deslizar X1 Y1 X2 Y2 [ms] | tecla CODIGO | texto HEX | sair.
 * Sem uso por 60 s, desconecta da acessibilidade (bateria; apps que estranham automação ligada).
 */
public class Tela {
    static UiAutomation ua;
    static HandlerThread fio;
    static volatile long ultimoUso = 0;
    static final long OCIOSO_MS = 60000;

    public static void main(String[] args) throws Exception {
        try {  // a acessibilidade cria Handlers no laço principal: ele precisa existir (como no uiautomator)
            Looper.prepareMainLooper();
        } catch (Throwable t) {
            // já preparado
        }
        final String pasta = args.length > 0 ? args[0] : "/sdcard/Download/.controle-ir-tela";
        String token = args.length > 1 ? args[1] : "x";
        new File(pasta, "pronto-" + token).createNewFile();
        Thread vigia = new Thread() {
            public void run() {
                while (true) {
                    try { Thread.sleep(5000); } catch (InterruptedException e) { return; }
                    synchronized (Tela.class) {
                        if (ua != null && System.currentTimeMillis() - ultimoUso > OCIOSO_MS) desconectar();
                    }
                }
            }
        };
        vigia.setDaemon(true);
        vigia.start();
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in, "UTF-8"));
        String linha;
        while ((linha = in.readLine()) != null) {
            linha = linha.trim();
            if (linha.length() == 0) continue;
            String[] p = linha.split(" ");
            String r;
            try {
                synchronized (Tela.class) {
                    ultimoUso = System.currentTimeMillis();
                    r = executar(p);
                }
            } catch (Throwable t) {
                r = "ERRO " + t;
            }
            responder(pasta, p[0], r);
            if (p.length > 1 && p[1].equals("sair")) break;
        }
        synchronized (Tela.class) { desconectar(); }
        System.exit(0);
    }

    static void responder(String pasta, String id, String r) throws Exception {
        File tmp = new File(pasta, id + ".tmp");
        OutputStream o = new FileOutputStream(tmp);
        o.write(r.getBytes("UTF-8"));
        o.close();
        tmp.renameTo(new File(pasta, id + ".r"));
    }

    static String executar(String[] p) throws Exception {
        String c = p.length > 1 ? p[1] : "";
        if (c.equals("ping") || c.equals("sair")) return "ok";
        UiAutomation u = conectar();
        if (c.equals("dump")) return dump(u);
        if (c.equals("foco")) {
            AccessibilityNodeInfo r = u.getRootInActiveWindow();
            return r == null || r.getPackageName() == null ? "" : r.getPackageName().toString();
        }
        if (c.equals("tocar")) {
            tocar(u, i(p[2]), i(p[3]), p.length > 4 ? i(p[4]) : 40);
            return "ok";
        }
        if (c.equals("deslizar")) {
            deslizar(u, i(p[2]), i(p[3]), i(p[4]), i(p[5]), p.length > 6 ? i(p[6]) : 300);
            return "ok";
        }
        if (c.equals("tecla")) {
            tecla(u, i(p[2]));
            return "ok";
        }
        if (c.equals("texto")) return texto(u, deHex(p.length > 2 ? p[2] : ""));
        return "ERRO comando desconhecido: " + c;
    }

    static int i(String s) { return Integer.parseInt(s); }

    // ------------------------------------------------------------------ conexão com a acessibilidade
    static UiAutomation conectar() throws Exception {
        if (ua != null) return ua;
        if (fio == null) {
            fio = new HandlerThread("controle-tela");
            fio.start();
        }
        Class<?> ccls = Class.forName("android.app.UiAutomationConnection");
        Constructor<?> cc = ccls.getDeclaredConstructor();
        cc.setAccessible(true);
        Object conexao = cc.newInstance();
        UiAutomation u = null;
        for (Constructor<?> k : UiAutomation.class.getDeclaredConstructors()) {
            Class<?>[] t = k.getParameterTypes();
            try {
                k.setAccessible(true);
                if (t.length == 2 && t[0] == Looper.class) { u = (UiAutomation) k.newInstance(fio.getLooper(), conexao); break; }
                if (t.length == 3 && t[0] == int.class && t[1] == Looper.class) {
                    u = (UiAutomation) k.newInstance(0, fio.getLooper(), conexao);
                    break;
                }
            } catch (Throwable e) {
                u = null;
            }
        }
        if (u == null) throw new RuntimeException("UiAutomation indisponivel");
        try {  // 1 = FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES: não desliga leitores de tela do usuário
            Method m = UiAutomation.class.getDeclaredMethod("connect", int.class);
            m.setAccessible(true);
            m.invoke(u, 1);
        } catch (NoSuchMethodException e) {
            Method m = UiAutomation.class.getDeclaredMethod("connect");
            m.setAccessible(true);
            m.invoke(u);
        }
        AccessibilityServiceInfo info = u.getServiceInfo();
        if (info != null) {  // inclui views "não importantes" e os ids, como o uiautomator
            info.flags |= AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS
                    | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;
            u.setServiceInfo(info);
        }
        ua = u;
        return u;
    }

    static void desconectar() {
        if (ua == null) return;
        try {
            Method m = UiAutomation.class.getDeclaredMethod("disconnect");
            m.setAccessible(true);
            m.invoke(ua);
        } catch (Throwable t) {
            // já caiu
        }
        ua = null;
    }

    // ------------------------------------------------------------------ leitura (mesmo XML do uiautomator dump)
    static String dump(UiAutomation u) {
        StringBuilder sb = new StringBuilder("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><hierarchy rotation=\"0\">");
        AccessibilityNodeInfo raiz = null;
        for (int t = 0; t < 3 && raiz == null; t++) {
            raiz = u.getRootInActiveWindow();
            if (raiz == null) SystemClock.sleep(80);
        }
        if (raiz != null) no(sb, raiz, 0);
        sb.append("</hierarchy>");
        return sb.toString();
    }

    static void no(StringBuilder sb, AccessibilityNodeInfo n, int d) {
        if (n == null || d > 80) return;
        Rect r = new Rect();
        n.getBoundsInScreen(r);
        sb.append("<node index=\"0\" text=\"").append(esc(n.getText()))
          .append("\" resource-id=\"").append(esc(n.getViewIdResourceName()))
          .append("\" class=\"").append(esc(n.getClassName()))
          .append("\" package=\"").append(esc(n.getPackageName()))
          .append("\" content-desc=\"").append(esc(n.getContentDescription()))
          .append("\" clickable=\"").append(n.isClickable())
          .append("\" long-clickable=\"").append(n.isLongClickable())
          .append("\" bounds=\"[").append(r.left).append(',').append(r.top).append("][")
          .append(r.right).append(',').append(r.bottom).append("]\">");
        int c = n.getChildCount();
        for (int k = 0; k < c; k++) {
            AccessibilityNodeInfo f = n.getChild(k);
            if (f != null) no(sb, f, d + 1);
        }
        sb.append("</node>");
    }

    static String esc(CharSequence cs) {
        if (cs == null) return "";
        StringBuilder sb = new StringBuilder();
        for (int k = 0; k < cs.length(); k++) {
            char ch = cs.charAt(k);
            switch (ch) {
                case '&': sb.append("&amp;"); break;
                case '<': sb.append("&lt;"); break;
                case '>': sb.append("&gt;"); break;
                case '"': sb.append("&quot;"); break;
                case '\n': sb.append("&#10;"); break;
                default:
                    if (ch >= 0x20 || ch == '\t') sb.append(ch);
            }
        }
        return sb.toString();
    }

    // ------------------------------------------------------------------ toques e teclas (injetados direto)
    static void evento(UiAutomation u, long desce, int acao, float x, float y) {
        MotionEvent e = MotionEvent.obtain(desce, SystemClock.uptimeMillis(), acao, x, y, 0);
        e.setSource(InputDevice.SOURCE_TOUCHSCREEN);
        u.injectInputEvent(e, true);
        e.recycle();
    }

    static void tocar(UiAutomation u, int x, int y, int ms) {
        long t = SystemClock.uptimeMillis();
        evento(u, t, MotionEvent.ACTION_DOWN, x, y);
        SystemClock.sleep(Math.max(10, Math.min(ms, 3000)));
        evento(u, t, MotionEvent.ACTION_UP, x, y);
    }

    static void deslizar(UiAutomation u, int x1, int y1, int x2, int y2, int ms) {
        long t = SystemClock.uptimeMillis();
        int passos = Math.max(5, Math.min(ms / 10, 100));
        evento(u, t, MotionEvent.ACTION_DOWN, x1, y1);
        for (int k = 1; k <= passos; k++) {
            SystemClock.sleep(Math.max(1, ms / passos));
            evento(u, t, MotionEvent.ACTION_MOVE, x1 + (x2 - x1) * k / (float) passos, y1 + (y2 - y1) * k / (float) passos);
        }
        evento(u, t, MotionEvent.ACTION_UP, x2, y2);
    }

    static void tecla(UiAutomation u, int codigo) {
        long t = SystemClock.uptimeMillis();
        KeyEvent d = new KeyEvent(t, t, KeyEvent.ACTION_DOWN, codigo, 0);
        d.setSource(InputDevice.SOURCE_KEYBOARD);
        u.injectInputEvent(d, true);
        KeyEvent s = new KeyEvent(t, SystemClock.uptimeMillis(), KeyEvent.ACTION_UP, codigo, 0);
        s.setSource(InputDevice.SOURCE_KEYBOARD);
        u.injectInputEvent(s, true);
    }

    static String texto(UiAutomation u, String s) {
        AccessibilityNodeInfo raiz = u.getRootInActiveWindow();
        AccessibilityNodeInfo campo = raiz == null ? null : raiz.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
        if (campo == null) return "ERRO nenhum campo de texto em foco";
        String atual = "";
        CharSequence ja = campo.getText();
        boolean dica = false;
        try {
            Method m = AccessibilityNodeInfo.class.getMethod("isShowingHintText");
            dica = (Boolean) m.invoke(campo);
        } catch (Throwable t) {
            // Android antigo
        }
        if (ja != null && !dica) atual = ja.toString();
        Bundle b = new Bundle();
        b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, atual + s);
        return campo.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b) ? "ok" : "ERRO o campo recusou o texto";
    }

    static String deHex(String h) throws Exception {
        byte[] b = new byte[h.length() / 2];
        for (int k = 0; k < b.length; k++) b[k] = (byte) Integer.parseInt(h.substring(2 * k, 2 * k + 2), 16);
        return new String(b, "UTF-8");
    }
}
