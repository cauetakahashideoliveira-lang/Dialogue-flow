package android.os;
public final class ParcelUuid {
    final String u;
    public ParcelUuid(String u) { this.u = u; }
    public static ParcelUuid curto(String quatro) { return new ParcelUuid("0000" + quatro + "-0000-1000-8000-00805F9B34FB"); }
    @Override public String toString() { return u; }
    @Override public boolean equals(Object o) { return o instanceof ParcelUuid && ((ParcelUuid) o).u.equals(u); }
    @Override public int hashCode() { return u.hashCode(); }
}
