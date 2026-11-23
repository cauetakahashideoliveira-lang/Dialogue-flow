package android.os;
import java.util.ArrayList;
import java.util.List;
public class Handler {
    static final List<Runnable> fila = new ArrayList<Runnable>();
    public Handler(Looper l) { if (l == null) throw new IllegalStateException("sem Looper principal"); }
    public boolean postDelayed(Runnable r, long ms) { fila.add(r); return true; }
}
