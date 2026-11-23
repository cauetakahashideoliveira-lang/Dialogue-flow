package android.os;
public final class Looper {
    static Looper principal;
    public static void prepareMainLooper() { principal = new Looper(); }
    public static Looper getMainLooper() { return principal; }
    public static void loop() {
        while (!Handler.fila.isEmpty()) Handler.fila.remove(0).run();
        throw new IllegalStateException("o laço terminou sem System.exit");
    }
}
