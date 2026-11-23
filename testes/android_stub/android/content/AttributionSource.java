package android.content;
public final class AttributionSource {
    public final int uid; public final String pacote;
    AttributionSource(int uid, String pacote) { this.uid = uid; this.pacote = pacote; }
    public static final class Builder {
        final int uid; String pacote;
        public Builder(int uid) { this.uid = uid; }
        public Builder setPackageName(String p) { pacote = p; return this; }
        public AttributionSource build() { return new AttributionSource(uid, pacote); }
    }
}
