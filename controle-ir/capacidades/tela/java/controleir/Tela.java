package controleir;

import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.UiAutomation;
import android.graphics.Bitmap;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.SystemClock;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.accessibility.AccessibilityEvent;
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
 * Comandos: ping | dump | foco | estado (pacote em foco e tela acesa, sem shell) | tocar X Y [ms] |
 * toques PAUSA_MS X1 Y1 X2 Y2… (vários toques num pedido só) | deslizar X1 Y1 X2 Y2 [ms] | tecla CODIGO | texto HEX |
 * calma QUIETO_MS LIMITE_MS (espera a tela parar de mudar; responde "ok MS" ou "tempo MS") |
 * eventos (contadores de janelas novas e de mudanças, relógio e a última janela: "J M T pacote|classe|texto") |
 * historico DESDE_MS (janelas surgidas depois de DESDE, uma por linha: "T pacote|classe|texto") |
 * toquesv PAUSA_MS X1 Y1… (como toques, mas para se surgir uma janela nova: "parou K pacote|classe|texto") |
 * aguardar M LIMITE_MS (espera o contador de mudanças sair de M; responde o contador atual) |
 * grade BX BY BL BA N PX PY PL PA K (lê uma grade NxN de algarismos desenhados, comparando cada casa com os K
 *   botões do teclado do próprio jogo; responde a grade em N linhas, 0 = vazia, e depois "duvidas i,j…") |
 * shell HEX (roda um comando como shell, sem abrir outra conexão com o Shizuku) |
 * foto LARGURA LIMITE_BYTES CAMINHO [X Y L A] (JPEG reduzido direto da acessibilidade, sem PNG nem ffmpeg) | sair.
 * Sem uso por 60 s, desconecta da acessibilidade (bateria; apps que estranham automação ligada); sem uso por 5 min,
 * encerra (o controle-ir abre de novo quando precisar).
 */
public class Tela {
    static UiAutomation ua;
    static HandlerThread fio;
    static volatile long ultimoUso = 0;
    // reflexos: contadores atualizados pelos eventos da acessibilidade (no fio dela, sem a trava dos comandos)
    static volatile int janelas = 0, mudancas = 0;
    static volatile String ultimaJanela = "||";
    static final String[] hist = new String[32];  // as últimas janelas surgidas, com a hora (anel)
    static volatile int histN = 0;
    static final long OCIOSO_MS = 60000, FIM_MS = 300000;

    public static void main(String[] args) throws Exception {
        try {  // a acessibilidade cria Handlers no laço principal: ele precisa existir (como no uiautomator)
            Looper.prepareMainLooper();
        } catch (Throwable t) {
            // já preparado
        }
        final String pasta = args.length > 0 ? args[0] : "/sdcard/Download/.controle-ir-tela";
        String token = args.length > 1 ? args[1] : "x";
        ultimoUso = System.currentTimeMillis();
        new File(pasta, "pronto-" + token).createNewFile();
        Thread vigia = new Thread() {
            public void run() {
                while (true) {
                    try { Thread.sleep(5000); } catch (InterruptedException e) { return; }
                    synchronized (Tela.class) {
                        long parado = System.currentTimeMillis() - ultimoUso;
                        if (ua != null && parado > OCIOSO_MS) desconectar();
                        if (parado > FIM_MS) System.exit(0);
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
        if (c.equals("shell")) return shell(deHex(p.length > 2 ? p[2] : ""), p.length > 3 ? i(p[3]) : 30000);
        UiAutomation u = conectar();
        if (c.equals("dump")) return dump(u);
        if (c.equals("foco")) return foco(u);
        if (c.equals("estado")) return foco(u) + "\n" + acesa();
        if (c.equals("tocar")) {
            tocar(u, i(p[2]), i(p[3]), p.length > 4 ? i(p[4]) : 40);
            return "ok";
        }
        if (c.equals("toques")) {
            int pausa = Math.max(0, Math.min(i(p[2]), 5000));
            for (int k = 3; k + 1 < p.length; k += 2) {
                if (k > 3 && pausa > 0) SystemClock.sleep(pausa);
                tocarLeva(u, i(p[k]), i(p[k + 1]), k + 3 >= p.length);
            }
            return "ok";
        }
        if (c.equals("eventos")) return janelas + " " + mudancas + " " + SystemClock.uptimeMillis() + " " + ultimaJanela;
        if (c.equals("historico")) {
            long desde = Long.parseLong(p[2]);
            StringBuilder sb = new StringBuilder();
            int n = histN;
            for (int k = Math.max(0, n - hist.length); k < n; k++) {
                String h = hist[k % hist.length];
                if (h != null && Long.parseLong(h.substring(0, h.indexOf(' '))) > desde) sb.append(h).append('\n');
            }
            return sb.toString();
        }
        if (c.equals("toquesv")) {
            int pausa = Math.max(0, Math.min(i(p[2]), 5000));
            int base = janelas, feitos = 0;
            for (int k = 3; k + 1 < p.length; k += 2) {
                if (k > 3 && pausa > 0) SystemClock.sleep(pausa);
                if (janelas != base) return "parou " + feitos + " " + ultimaJanela;
                tocarLeva(u, i(p[k]), i(p[k + 1]), k + 3 >= p.length);
                feitos++;
            }
            SystemClock.sleep(Math.max(pausa, 30));  // o efeito do último toque também conta
            return janelas != base ? "parou " + feitos + " " + ultimaJanela : "ok";
        }
        if (c.equals("aguardar")) {
            int m = i(p[2]);
            long fim = SystemClock.uptimeMillis() + Math.max(10, Math.min(i(p[3]), 30000));
            while (mudancas == m && SystemClock.uptimeMillis() < fim) SystemClock.sleep(10);
            return String.valueOf(mudancas);
        }
        if (c.equals("grade")) {
            int[] b = {i(p[2]), i(p[3]), i(p[4]), i(p[5])}, t = {i(p[7]), i(p[8]), i(p[9]), i(p[10])};
            return grade(u, b, i(p[6]), t, i(p[11]));
        }
        if (c.equals("calma")) {
            long t0 = SystemClock.uptimeMillis();
            try {
                u.waitForIdle(Math.max(20, i(p[2])), Math.max(50, Math.min(i(p[3]), 10000)));
                return "ok " + (SystemClock.uptimeMillis() - t0);
            } catch (java.util.concurrent.TimeoutException e) {
                return "tempo " + (SystemClock.uptimeMillis() - t0);
            }
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
        if (c.equals("foto")) {
            int[] rec = p.length > 8 ? new int[]{i(p[5]), i(p[6]), i(p[7]), i(p[8])} : null;
            return foto(u, i(p[2]), i(p[3]), p[4], rec);
        }
        return "ERRO comando desconhecido: " + c;
    }

    static int i(String s) { return Integer.parseInt(s); }

    static String limpo(CharSequence cs, int max) {
        if (cs == null) return "";
        String t = cs.toString().replace('|', '/').replace('\n', ' ').replace('\r', ' ');
        return t.length() > max ? t.substring(0, max) : t;
    }

    static String foco(UiAutomation u) {
        AccessibilityNodeInfo r = null;
        for (int t = 0; t < 4 && r == null; t++) {
            r = u.getRootInActiveWindow();
            if (r == null) SystemClock.sleep(60);
        }
        return r == null || r.getPackageName() == null ? "" : r.getPackageName().toString();
    }

    /** Tela acesa pelo PowerManager do sistema (o mesmo do `dumpsys power`), sem abrir um shell: "1", "0" ou "?". */
    static String acesa() {
        try {
            Object b = Class.forName("android.os.ServiceManager").getMethod("getService", String.class)
                    .invoke(null, "power");
            Object pm = Class.forName("android.os.IPowerManager$Stub").getMethod("asInterface", android.os.IBinder.class)
                    .invoke(null, b);
            return ((Boolean) pm.getClass().getMethod("isInteractive").invoke(pm)) ? "1" : "0";
        } catch (Throwable t) {
            return "?";
        }
    }

    // ------------------------------------------------------------------ comandos de shell (screencap, dumpsys…)
    /** Resposta: "rc tamanho_saida\n" + saída + erros (a saída e os erros vêm separados pelo tamanho). */
    static String shell(String cmd, int limiteMs) throws Exception {
        final Process pr = Runtime.getRuntime().exec(new String[]{"sh", "-c", cmd});
        pr.getOutputStream().close();
        final java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream(), err = new java.io.ByteArrayOutputStream();
        Thread a = copiar(pr.getInputStream(), out), b = copiar(pr.getErrorStream(), err);
        long fim = System.currentTimeMillis() + limiteMs;
        int rc = -1;
        while (true) {
            try { rc = pr.exitValue(); break; } catch (IllegalThreadStateException e) { /* ainda rodando */ }
            if (System.currentTimeMillis() > fim) { pr.destroy(); rc = 124; break; }
            SystemClock.sleep(5);
        }
        a.join(2000);
        b.join(2000);
        String so = out.toString("UTF-8");
        return rc + " " + so.length() + "\n" + so + err.toString("UTF-8");
    }

    static Thread copiar(final java.io.InputStream in, final java.io.ByteArrayOutputStream dest) {
        Thread t = new Thread() {
            public void run() {
                byte[] buf = new byte[65536];
                int n;
                try { while ((n = in.read(buf)) > 0) dest.write(buf, 0, n); } catch (Exception e) { /* fim */ }
            }
        };
        t.start();
        return t;
    }

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
        u.setOnAccessibilityEventListener(new UiAutomation.OnAccessibilityEventListener() {
            public void onAccessibilityEvent(AccessibilityEvent e) {
                mudancas++;
                if (e.getEventType() == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
                    String t = "";
                    if (e.getText() != null && !e.getText().isEmpty() && e.getText().get(0) != null) t = e.getText().get(0).toString();
                    ultimaJanela = limpo(e.getPackageName(), 80) + "|" + limpo(e.getClassName(), 120) + "|" + limpo(t, 80);
                    hist[histN % hist.length] = SystemClock.uptimeMillis() + " " + ultimaJanela;
                    histN++;
                    janelas++;
                }
            }
        });
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
          .append("\" checkable=\"").append(n.isCheckable())
          .append("\" checked=\"").append(n.isChecked())
          .append("\" selected=\"").append(n.isSelected())
          .append("\" scrollable=\"").append(n.isScrollable())
          .append("\" focused=\"").append(n.isFocused())
          .append("\" enabled=\"").append(n.isEnabled())
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
        evento(u, desce, acao, x, y, true);
    }

    /** sync=true espera o app consumir o evento (~20–40 ms); false só entrega à fila de entrada, que mantém a ordem. */
    static void evento(UiAutomation u, long desce, int acao, float x, float y, boolean sync) {
        MotionEvent e = MotionEvent.obtain(desce, SystemClock.uptimeMillis(), acao, x, y, 0);
        e.setSource(InputDevice.SOURCE_TOUCHSCREEN);
        u.injectInputEvent(e, sync);
        e.recycle();
    }

    static void tocar(UiAutomation u, int x, int y, int ms) {
        long t = SystemClock.uptimeMillis();
        evento(u, t, MotionEvent.ACTION_DOWN, x, y);
        SystemClock.sleep(Math.max(10, Math.min(ms, 3000)));
        evento(u, t, MotionEvent.ACTION_UP, x, y);
    }

    /** Toque de leva: direto no gerenciador de entrada (sem a UiAutomation, que espera as animações do app a cada
     *  evento), sem esperar a confirmação (a fila preserva a ordem); só o último espera o app consumir. */
    static void tocarLeva(UiAutomation u, int x, int y, boolean ultimo) {
        long t = SystemClock.uptimeMillis();
        direto(u, t, MotionEvent.ACTION_DOWN, x, y, false);
        SystemClock.sleep(LEVA_MS);
        direto(u, t, MotionEvent.ACTION_UP, x, y, ultimo);
    }

    static Object entrada;  // InputManagerGlobal (Android 14+) ou InputManager
    static Method injetar;
    static boolean semDireto = false;

    static void direto(UiAutomation u, long desce, int acao, float x, float y, boolean esperar) {
        if (!semDireto) {
            try {
                if (injetar == null) {
                    try {
                        Class<?> g = Class.forName("android.hardware.input.InputManagerGlobal");
                        entrada = g.getMethod("getInstance").invoke(null);
                    } catch (Throwable t) {
                        Class<?> g = Class.forName("android.hardware.input.InputManager");
                        entrada = g.getMethod("getInstance").invoke(null);
                    }
                    injetar = entrada.getClass().getMethod("injectInputEvent", android.view.InputEvent.class, int.class);
                }
                MotionEvent e = MotionEvent.obtain(desce, SystemClock.uptimeMillis(), acao, x, y, 0);
                e.setSource(InputDevice.SOURCE_TOUCHSCREEN);
                Object ok = injetar.invoke(entrada, e, esperar ? 2 : 0);  // 2 = esperar o app consumir; 0 = assíncrono
                e.recycle();
                if (Boolean.TRUE.equals(ok)) return;
                semDireto = true;  // recusado (ex.: sem permissão de injetar): daqui em diante, pela UiAutomation
            } catch (Throwable t) {
                semDireto = true;  // sem o caminho direto neste Android: fica a UiAutomation
            }
        }
        evento(u, desce, acao, x, y, esperar);
    }

    static final int LEVA_MS = 12;  // pressão de cada toque da leva (qualquer app reconhece um toque a partir de ~5 ms)

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

    // ------------------------------------------------------------------ captura (JPEG direto)
    /** Resposta: "LARGURA_REAL ALTURA_REAL BYTES" (ou ERRO). O JPEG vai para CAMINHO (pasta de troca). */
    static String foto(UiAutomation u, int largura, int limite, String caminho, int[] rec) throws Exception {
        Bitmap b = u.takeScreenshot();
        if (b == null) return "ERRO sem captura (tela apagada ou protegida)";
        int lw = b.getWidth(), lh = b.getHeight();
        Bitmap soft = b.copy(Bitmap.Config.ARGB_8888, false);  // capturas novas vêm em memória de vídeo
        b.recycle();
        Bitmap base = soft;
        if (rec != null) {
            int x = Math.max(0, Math.min(rec[0], lw - 1)), y = Math.max(0, Math.min(rec[1], lh - 1));
            int w = Math.max(1, Math.min(rec[2], lw - x)), h = Math.max(1, Math.min(rec[3], lh - y));
            base = Bitmap.createBitmap(soft, x, y, w, h);
        }
        int w = Math.min(largura, base.getWidth());
        int h = Math.max(1, Math.round(base.getHeight() * (w / (float) base.getWidth())));
        Bitmap red = (w == base.getWidth()) ? base : Bitmap.createScaledBitmap(base, w, h, true);
        byte[] dados = null;
        int[] qualidades = {80, 65, 50, 35};
        for (int q : qualidades) {
            java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
            red.compress(Bitmap.CompressFormat.JPEG, q, bo);
            dados = bo.toByteArray();
            if (dados.length <= limite) break;
        }
        File tmp = new File(caminho + ".tmp");
        OutputStream o = new FileOutputStream(tmp);
        o.write(dados);
        o.close();
        tmp.renameTo(new File(caminho));
        if (red != base) red.recycle();
        if (base != soft) base.recycle();
        soft.recycle();
        return lw + " " + lh + " " + dados.length;
    }

    // ------------------------------------------------------------------ leitura de grade (sem OCR: modelos do teclado)
    static final int S = 16;

    static String grade(UiAutomation u, int[] b, int n, int[] t, int k) {
        Bitmap cap = u.takeScreenshot();
        if (cap == null) return "ERRO sem captura";
        Bitmap bm = cap.copy(Bitmap.Config.ARGB_8888, false);
        cap.recycle();
        int[][] mod = new int[k][];
        for (int d = 0; d < k; d++) {  // o algarismo grande fica na parte de cima do botão (embaixo vem a contagem)
            int x = t[0] + d * t[2] / k, w = t[2] / k;
            mod[d] = assinatura(bm, x + w / 8, t[1], w - w / 4, t[3] * 62 / 100);
        }
        StringBuilder out = new StringBuilder(), duv = new StringBuilder();
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                int x = b[0] + c * b[2] / n, y = b[1] + r * b[3] / n, w = b[2] / n, h = b[3] / n;
                int[] a = assinatura(bm, x + w / 8, y + h / 8, w - w / 4, h - h / 4);
                if (a == null) { out.append('0'); continue; }
                int melhor = -1, d1 = Integer.MAX_VALUE, d2 = Integer.MAX_VALUE;
                for (int d = 0; d < k; d++) {
                    if (mod[d] == null) continue;
                    int dist = 0;
                    for (int q = 0; q < S * S; q++) dist += Math.abs(a[q] - mod[d][q]);
                    if (dist < d1) { d2 = d1; d1 = dist; melhor = d; } else if (dist < d2) d2 = dist;
                }
                out.append(melhor < 0 ? '?' : (char) ('1' + melhor));
                if (melhor < 0 || d2 - d1 < 12) duv.append(r).append(',').append(c).append(' ');
            }
            out.append('\n');
        }
        bm.recycle();
        return out.append("duvidas ").append(duv.toString().trim()).toString();
    }

    /** Desenho de uma casa reduzido a 16x16 (1 = tinta), enquadrado pela tinta; null se a casa está vazia.
     *  Tinta = bem mais escura que o fundo da casa (o fundo é lido nas bordas: casa destacada também funciona). */
    static int[] assinatura(Bitmap bm, int x, int y, int w, int h) {
        x = Math.max(0, x); y = Math.max(0, y);
        w = Math.min(w, bm.getWidth() - x); h = Math.min(h, bm.getHeight() - y);
        if (w < 4 || h < 4) return null;
        int[] px = new int[w * h];
        bm.getPixels(px, 0, w, x, y, w, h);
        int[] lum = new int[w * h];
        for (int q = 0; q < px.length; q++) {
            int v = px[q];
            lum[q] = (((v >> 16) & 255) * 30 + ((v >> 8) & 255) * 59 + (v & 255) * 11) / 100;
        }
        long soma = 0; int nb = 0;
        for (int q = 0; q < w; q++) { soma += lum[q] + lum[(h - 1) * w + q]; nb += 2; }
        for (int q = 0; q < h; q++) { soma += lum[q * w] + lum[q * w + w - 1]; nb += 2; }
        int lim = (int) (soma / nb) - 60;
        int x0 = w, y0 = h, x1 = -1, y1 = -1, tinta = 0;
        for (int yy = 0; yy < h; yy++) for (int xx = 0; xx < w; xx++) if (lum[yy * w + xx] < lim) {
            tinta++;
            if (xx < x0) x0 = xx; if (xx > x1) x1 = xx; if (yy < y0) y0 = yy; if (yy > y1) y1 = yy;
        }
        if (tinta < w * h / 60 || x1 < 0) return null;
        int bw = x1 - x0 + 1, bh = y1 - y0 + 1, lado = Math.max(bw, bh);
        int ox = x0 - (lado - bw) / 2, oy = y0 - (lado - bh) / 2;  // quadrado centrado: "1" não vira bloco
        int[] sig = new int[S * S];
        for (int sy = 0; sy < S; sy++) for (int sx = 0; sx < S; sx++) {
            int ax = ox + sx * lado / S, ay = oy + sy * lado / S, bx = ox + (sx + 1) * lado / S, by = oy + (sy + 1) * lado / S;
            int tot = 0, sim = 0;
            for (int yy = Math.max(ay, 0); yy < Math.min(by, h); yy++)
                for (int xx = Math.max(ax, 0); xx < Math.min(bx, w); xx++) { tot++; if (lum[yy * w + xx] < lim) sim++; }
            sig[sy * S + sx] = tot > 0 && sim * 4 > tot ? 1 : 0;
        }
        return sig;
    }

    static String deHex(String h) throws Exception {
        byte[] b = new byte[h.length() / 2];
        for (int k = 0; k < b.length; k++) b[k] = (byte) Integer.parseInt(h.substring(2 * k, 2 * k + 2), 16);
        return new String(b, "UTF-8");
    }
}
