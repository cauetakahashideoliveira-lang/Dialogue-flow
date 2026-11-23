package android.bluetooth;
public final class BluetoothDevice {
    final String end, nome; final int tipo; final BluetoothClass classe;
    public BluetoothDevice(String end, String nome, int tipo, BluetoothClass c) { this.end = end; this.nome = nome; this.tipo = tipo; classe = c; }
    public String getAddress() { return end; }
    public String getName() { if (nome == null) throw new SecurityException("sem BLUETOOTH_CONNECT"); return nome; }
    public int getType() { return tipo; }
    public BluetoothClass getBluetoothClass() { return classe; }
}
