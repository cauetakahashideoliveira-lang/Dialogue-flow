package android.bluetooth;
import android.bluetooth.le.BluetoothLeScanner;
import android.content.AttributionSource;
import java.util.LinkedHashSet;
import java.util.Set;
public final class BluetoothAdapter {
    static final String MODO = System.getProperty("stub.modo", "ligado");
    boolean le = false;
    final String pacote;
    BluetoothAdapter(String pacote) { this.pacote = pacote; }
    static BluetoothAdapter createAdapter(AttributionSource a) { System.err.println("criado como " + a.pacote + " uid " + a.uid); return new BluetoothAdapter(a.pacote); }
    public static BluetoothAdapter getDefaultAdapter() { return new BluetoothAdapter(null); }
    public boolean isEnabled() { return MODO.equals("ligado") || MODO.equals("falha"); }
    public boolean isLeEnabled() { return le; }
    public boolean enableBLE() { if (MODO.equals("desligado_ble")) { le = true; System.err.println("enableBLE"); return true; } return false; }
    public boolean disableBLE() { le = false; System.err.println("disableBLE"); return true; }
    public Set<BluetoothDevice> getBondedDevices() {
        if (!"com.android.shell".equals(pacote)) throw new SecurityException("pacote errado");
        Set<BluetoothDevice> s = new LinkedHashSet<BluetoothDevice>();
        s.add(new BluetoothDevice("AA:AA:AA:AA:AA:01", "JBL Flip 5", 3, new BluetoothClass(0x0400, 0x0414)));
        s.add(new BluetoothDevice("AA:AA:AA:AA:AA:02", "Redmi Watch", 2, null));
        return s;
    }
    public BluetoothLeScanner getBluetoothLeScanner() { return (isEnabled() || le) ? new BluetoothLeScanner(pacote) : null; }
}
